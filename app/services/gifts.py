import asyncio
from typing import List, Dict, Any
from loguru import logger

from app.loader import bot
from app.database.crud.gift_sql import get_active_purchase_settings
from app.database.crud.user import decrease_user_balance
from app.services.error_handler import handle_errors


class GiftService:
    def __init__(self):
        self.is_running = False
        self.is_distributing = False  # Флаг для отслеживания состояния рассылки

    @handle_errors("Получение доступных подарков")
    async def get_available_gifts(self) -> List[Dict[str, Any]]:
        """Получить список доступных подарков через Telegram API"""
        result = await bot.get_available_gifts()
        if result and result.gifts:
            gifts = [
                {
                    "id": gift.id,
                    "price": gift.star_count,
                    "upgrade_price": gift.upgrade_star_count,
                    "total_count": gift.total_count,
                    "remaining_count": gift.remaining_count
                }
                for gift in result.gifts
            ]
            # logger.info(f"Найдены подарки: {[{'id': gift['id'], 'price': gift['price'], 'total_count': gift['total_count']} for gift in gifts]}")
            return gifts
        return []

    @handle_errors("Обработка уникальных подарков")
    async def process_unique_gifts(self, gifts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обработка уникальных подарков"""
        # Закомментирована проверка на уникальность
        unique_gifts = [
            {
                "id": gift["id"],
                "price": gift["price"],
                "upgrade_price": gift["upgrade_price"],
                "total_count": gift["total_count"],
                "remaining_count": gift["remaining_count"]
            }
            for gift in gifts 
            if gift.get("total_count") is not None and gift["total_count"] > 0
        ]
        
        if unique_gifts:
            logger.info(f"Найдены уникальные подарки: {[gift['id'] for gift in unique_gifts]}")
            return unique_gifts
        return []

    @handle_errors("Рассылка подарков")
    async def distribute_gifts(self, unique_gifts: List[Dict[str, Any]]) -> None:
        """Рассылка уникальных подарков"""
        logger.info("Начинаем рассылку уникальных подарков")
        
        # Получаем активные настройки автопокупки с балансом
        users_with_settings = await get_active_purchase_settings()
        
        if not users_with_settings:
            logger.info("Нет активных пользователей для автопокупки")
            return
            
        # Флаг для отслеживания успешных отправок
        gifts_sent = False
        
        # Обрабатываем каждого пользователя
        for settings, balance in users_with_settings:
            logger.info(f"Обрабатываем пользователя {settings.user_id} с балансом {balance}")
            
            # Фильтруем подарки по настройкам пользователя
            suitable_gifts = self._filter_gifts_for_user(unique_gifts, settings)
            
            if not suitable_gifts:
                logger.info(f"Для пользователя {settings.user_id} нет подходящих подарков")
                continue
                
            # Рассчитываем и покупаем подарки
            total_spent = await self._purchase_gifts_for_user(settings, suitable_gifts, balance)
            
            if total_spent > 0:
                await bot.send_message(settings.user_id, f"Подарки успешно куплены на сумму {total_spent} звезд")
                logger.info(f"Пользователь {settings.user_id} потратил {total_spent} звезд")
                gifts_sent = True  # Отмечаем, что подарки были отправлены
            else:
                await bot.send_message(settings.user_id, f"Недостаточно средств для покупки подарков")
                logger.info(f"Пользователь {settings.user_id} не смог купить подарки")
        
        # Пауза только если были отправлены подарки
        if gifts_sent:
            await asyncio.sleep(60)
            logger.info("Рассылка завершена, пауза 60 секунд")
        else:
            logger.info("Подарки не были отправлены, пауза не нужна")

    @handle_errors("Фильтрация подарков")
    def _filter_gifts_for_user(self, gifts: List[Dict[str, Any]], settings) -> List[Dict[str, Any]]:
        """Фильтрует подарки по настройкам пользователя"""
        suitable_gifts = []
        
        for gift in gifts:
            price = gift["price"]
            total_count = gift["total_count"]
            
            # Проверяем минимальную цену (0 = без ограничений)
            if settings.min_price > 0 and price < settings.min_price:
                continue
                
            # Проверяем максимальную цену (0 = без ограничений)
            if settings.max_price > 0 and price > settings.max_price:
                continue
                
            # Проверяем лимит саплая (0 = без ограничений)
            if settings.supply_limit > 0 and total_count > settings.supply_limit:
                continue
                
            suitable_gifts.append(gift)
            
        logger.info(f"Для пользователя {settings.user_id} подходят подарки: {[g['id'] for g in suitable_gifts]}")
        return suitable_gifts

    @handle_errors("Покупка подарков")
    async def _purchase_gifts_for_user(self, settings, gifts: List[Dict[str, Any]], balance: int) -> int:
        """Покупает подарки для пользователя и возвращает потраченную сумму"""
        if not gifts:
            return 0
            
        # Рассчитываем общую стоимость всех подарков за один цикл
        cycle_cost = sum(gift["price"] for gift in gifts)
        
        # Проверяем, хватает ли денег хотя бы на один цикл
        if balance < cycle_cost:
            # Проверяем, можем ли купить хотя бы один самый дешевый подарок
            min_price = min(gift["price"] for gift in gifts)
            if balance < min_price:
                logger.info(f"У пользователя {settings.user_id} недостаточно средств даже на самый дешевый подарок")
                return 0
        
        total_spent = 0
        gifts_to_send = []  # Список подарков для отправки
        
        # Проходим циклы покупки
        for cycle in range(settings.purchase_cycles):
            cycle_gifts = []
            cycle_spent = 0
            
            # Пытаемся купить каждый подарок в текущем цикле
            for gift in gifts:
                gift_price = gift["price"]
                
                # Проверяем, хватает ли денег на этот подарок
                if balance >= gift_price:
                    cycle_gifts.append({
                        "id": gift["id"],
                        "price": gift_price,
                        "user_id": settings.user_id
                    })
                    cycle_spent += gift_price
                    balance -= gift_price
                    
            if cycle_gifts:
                gifts_to_send.extend(cycle_gifts)
                total_spent += cycle_spent
                logger.info(f"Цикл {cycle + 1}: куплено {len(cycle_gifts)} подарков на {cycle_spent} звезд")
            else:
                logger.info(f"Цикл {cycle + 1}: недостаточно средств для покупки подарков")
                break
        
        # Отправляем подарки пользователю
        if gifts_to_send:
            await self._send_gifts_to_user(settings.user_id, gifts_to_send)
            
            # Списываем потраченную сумму с баланса
            if total_spent > 0:
                await decrease_user_balance(settings.user_id, total_spent)
                logger.info(f"Списано {total_spent} звезд с баланса пользователя {settings.user_id}")
        
        return total_spent

    @handle_errors("Отправка подарков")
    async def _send_gifts_to_user(self, user_id: int, gifts: List[Dict[str, Any]]) -> None:
        """Отправляет подарки пользователю через Telegram API"""
        for gift in gifts:
            max_attempts = 60
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    await bot.send_gift(gift["id"], user_id, text=f"@vityooook love u")
                    logger.info(f"Отправлен подарок {gift['id']} пользователю {user_id} за {gift['price']} звезд")
                    break  # Успешная отправка, выходим из цикла
                except Exception as e:
                    attempt += 1
                    if attempt == max_attempts:
                        logger.error(f"Не удалось отправить подарк {gift['id']} пользователю {user_id} после {max_attempts} попыток: {e}")
                        raise  # Если все попытки исчерпаны, пробрасываем ошибку дальше
                    else:
                        logger.warning(f"Попытка {attempt} отправки подарка {gift['id']} не удалась. Повторная попытка через 1 секунду")
                        await asyncio.sleep(1)  # Пауза 1 секунда между попытками
                        continue

    @handle_errors("Проверка и покупка подарков")
    async def check_and_purchase_gifts(self) -> None:
        """Проверка доступных подарков"""
        self.is_running = True
        while self.is_running:
            try:
                if not self.is_distributing:
                    available_gifts = await self.get_available_gifts()
                    if available_gifts:
                        unique_gifts = await self.process_unique_gifts(available_gifts)
                        if unique_gifts:
                            self.is_distributing = True
                            await self.distribute_gifts(unique_gifts)
                            self.is_distributing = False
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Ошибка в check_and_purchase_gifts: {e}")
                await asyncio.sleep(1)

    def stop(self):
        """Остановить сервис"""
        self.is_running = False

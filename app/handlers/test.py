from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import CommandObject
from aiogram.filters import Command
from loguru import logger
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError

from app.database.crud.user import get_user_balance, is_admin, decrease_user_balance
from app.keyboards.main_kb import get_main_menu
from app.loader import bot

router = Router()
 

@router.message(Command("test"))
async def cmd_test(message: Message, command: CommandObject) -> None:
    """Обработчик тестовой команды для покупки подарка"""
    try:
        # Проверка на админа
        if not await is_admin(message.from_user.id):
            await message.answer(
                "❌ У вас нет доступа к этой команде. "
                "Пожалуйста, обратитесь к администратору."
            )
            return
        
        # Проверка аргументов
        if not command.args:
            await message.answer(
                "Использование: /test <stars_price_gift>\n"
                "Пример: /test 100"
            )
            return

        try:
            # Получаем список доступных подарков
            gifts = await bot.get_available_gifts()
            gifts_list = gifts.gifts
            logger.info(f"Found {len(gifts_list)} available gifts")
            
            # Получаем баланс пользователя
            balance = await get_user_balance(message.from_user.id)
            logger.info(f"User balance: {balance}")

            # Проверяем достаточность средств
            try:
                gift_price = int(command.args)
            except ValueError:
                await message.answer(
                    "❌ Ошибка: Некорректная сумма подарка.\n"
                    "Используйте только числа."
                )
                return

            if balance < gift_price:
                await message.answer(
                    f"❌ У вас недостаточно звезд для покупки подарка.\n"
                    f"Требуется: {gift_price}\n"
                    f"Ваш баланс: {balance}"
                )
                return
            
            # Ищем подарок с указанной ценой
            gift_found = False
            for gift in gifts_list:
                if gift.star_count == gift_price:
                    # Проверяем доступность ограниченного подарка
                    if hasattr(gift, 'remaining_count') and gift.remaining_count is not None:
                        if gift.remaining_count <= 0:
                            logger.warning(f"Gift {gift.id} is out of stock")
                            continue
                        logger.info(f"Gift {gift.id}")
                    
                    gift_found = True
                    logger.info(f"Found gift with price {gift_price}, id: {gift.id}")
                    
                    try:
                        # Отправляем подарок
                        await bot.send_gift(
                            gift.id,
                            message.from_user.id,
                            text=f"Gift from @vityooook"
                        )
                        logger.info("Gift sent successfully")
                        
                        # Уменьшаем баланс
                        await decrease_user_balance(message.from_user.id, gift_price)
                        logger.info(f"User balance decreased by {gift_price}")
                        
                        await message.answer(
                            f"✅ Подарок стоимостью {gift_price} звезд успешно отправлен!\n"
                            f"Новый баланс: {balance - gift_price}",
                            reply_markup=get_main_menu()
                        )
                        logger.info(f"Successfully processed gift purchase for user {message.from_user.id}")
                        return
                        
                    except ValidationError as e:
                        logger.error(f"Validation error while sending gift: {e}")
                        await message.answer(
                            "❌ Ошибка при отправке подарка. Попробуйте позже."
                        )
                        return
                    except Exception as e:
                        logger.error(f"Error while sending gift: {e}")
                        await message.answer(
                            "❌ Ошибка при отправке подарка. Попробуйте позже."
                        )
                        return
            
            if not gift_found:
                # Формируем список доступных цен с учетом ограничений
                available_prices = []
                for gift in gifts_list:
                    if hasattr(gift, 'remaining_count') and gift.remaining_count is not None:
                        if gift.remaining_count > 0:
                            available_prices.append(f"{gift.star_count} (осталось: {gift.remaining_count})")
                    else:
                        available_prices.append(str(gift.star_count))
                
                await message.answer(
                    f"❌ Подарок стоимостью {gift_price} звезд не найден или закончился.\n"
                    f"Доступные цены: {', '.join(available_prices) if available_prices else 'нет доступных подарков'}"
                )
                return

        except Exception as e:
            logger.error(f"Unexpected error in gift purchase: {e}")
            await message.answer(
                "❌ Произошла непредвиденная ошибка. Попробуйте позже.",
                reply_markup=get_main_menu()
            )

    except Exception as e:
        logger.error(f"Error in test command: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке команды. Попробуйте позже.",
            reply_markup=get_main_menu()
        )

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import CommandObject
from aiogram.filters import Command
from loguru import logger
from aiogram.fsm.context import FSMContext

from app.database.crud.user import (
    get_user_balance,
    delete_transaction,
    decrease_user_balance
)
from app.keyboards.main_kb import get_main_menu
from app.loader import bot

router = Router()
 

@router.message(Command("refund"))
async def cmd_refund(message: Message, command: CommandObject) -> None:
    """Обработчик команды возврата средств"""
    try:
        if not command.args:
            await message.answer(
                "Использование: /refund <transaction_id>\n"
                "Пример: /refund 123456789"
            )
            return

        logger.info(f"Processing refund request for transaction {command.args}")

        try:
            # Получаем сумму транзакции и удаляем её
            amount = await delete_transaction(command.args)
            logger.info(f"Transaction deleted, amount: {amount}")
            
            # Уменьшаем баланс пользователя
            await decrease_user_balance(message.from_user.id, amount)
            logger.info(f"User balance decreased by {amount}")
            
            # Выполняем возврат через Telegram API
            await bot.refund_star_payment(message.from_user.id, command.args)
            logger.info("Telegram API refund completed")
            
            await message.answer(
                f"✅ Возврат {amount} звезд прошел успешно!",
                reply_markup=get_main_menu()
            )
            logger.info(f"Successfully processed refund for user {message.from_user.id}")

        except ValueError as e:
            error_message = str(e)
            if "Transaction not found" in error_message:
                await message.answer("❌ Транзакция не найдена")
            elif "Insufficient balance" in error_message:
                await message.answer("❌ Недостаточно звезд для возврата")
            else:
                await message.answer(f"❌ Ошибка: {error_message}")
            logger.warning(f"Refund validation error: {e}")

    except Exception as e:
        logger.error(f"Error in refund command: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке возврата. Попробуйте позже.",
            reply_markup=get_main_menu()
        )

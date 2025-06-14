from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from loguru import logger
from aiogram.fsm.context import FSMContext

from app.database.crud.user import get_or_create_user, get_user_balance, is_admin
from app.keyboards.main_kb import get_main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start

    :param message: Сообщение от пользователя
    """
    try:
        # Сначала создаем/получаем пользователя
        user = await get_or_create_user(
            user_id=message.from_user.id,
            username=message.from_user.username
        )
        
        # Проверяем является ли пользователь админом
        if not await is_admin(message.from_user.id):
            await message.answer(
                "У вас нет доступа к боту. "
                "Пожалуйста, обратитесь к администратору."
            )
            return
        
        await state.clear()
        
        balance = await get_user_balance(message.from_user.id)
            
        await message.answer(
            f"Привет, {message.from_user.full_name}! 👋\n\n"
            f"💰 Баланс: {balance} ⭐️\n\n"
            "Я бот для автоматической покупки подарков в Telegram.",
            reply_markup=get_main_menu()
        )
        logger.info(f"User {message.from_user.id} started the bot")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработчик возврата в главное меню

    :param callback: Callback запрос
    """
    try:
        # Проверяем является ли пользователь админом
        if not await is_admin(callback.from_user.id):
            await callback.message.edit_text(
                "У вас нет доступа к боту. "
                "Пожалуйста, обратитесь к администратору."
            )
            return

        await state.clear()
        
        balance = await get_user_balance(callback.from_user.id)
        
        await callback.message.edit_text(
            f"Главное меню:\n\n"
            f"💰 Баланс: {balance} ⭐️",
            reply_markup=get_main_menu()
        )
        logger.info(f"User {callback.from_user.id} returned to main menu")
    except Exception as e:
        logger.error(f"Error returning to main menu: {e}")
        await callback.message.edit_text(
            "Произошла ошибка. Попробуйте позже.",
            reply_markup=get_main_menu()
        ) 
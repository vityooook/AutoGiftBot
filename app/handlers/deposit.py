from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.loader import bot

from loguru import logger

from app.database.crud.user import get_or_create_user, update_user_balance, get_user_balance
from app.keyboards.main_kb import get_main_menu
from app.keyboards.deposit_kb import get_back_to_main, get_payment_keyboard

router = Router()

class DepositStates(StatesGroup):
    amount = State()

@router.callback_query(F.data == "deposit")
async def process_deposit(query: CallbackQuery, state: FSMContext) -> None:
    """Обработка пополнения баланса"""

    await query.message.edit_text(
        "Введите сумму пополнения:",
        reply_markup=get_back_to_main()
    )
    await state.set_state(DepositStates.amount)


@router.message(DepositStates.amount)
async def process_amount(message: Message, state: FSMContext) -> None:
    """Обработка введенной суммы"""
    amount = message.text
    if not amount.isdigit():
        await message.answer("Введите сумму пополнения в виде числа!", reply_markup=get_back_to_main())
        return
    
    await state.clear()
    
    try:
        invoice = await bot.create_invoice_link(
            title="Пополнение баланса",
            description="Пополните баланс для автоматической покупки подарков",
            provider_token="",  # Здесь нужно указать ваш токен от @BotFather
            currency="XTR",
            prices=[LabeledPrice(label="Пополнение баланса", amount=int(amount))],
            payload="top_up_stars"
        )
        
        
        await message.answer(
            "💳 Для пополнения баланса перейдите по ссылке ниже:",
            reply_markup=get_payment_keyboard(int(amount), invoice)
        )
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при создании платежа. Попробуйте позже.",
            reply_markup=get_back_to_main()
        )

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery) -> None:
    """Обработка предварительного запроса на оплату"""
    await pre_checkout_query.answer(
        ok=True,
        error_message="Произошла ошибка при оплате. Попробуйте позже."
    )

@router.message(F.successful_payment)
async def process_successful_payment(message: Message) -> None:
    """Обработка успешной оплаты"""

    await update_user_balance(
        user_id=message.from_user.id,
        amount=message.successful_payment.total_amount,
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id
    )

    await message.answer(f"твой чек на возрат: {message.successful_payment.telegram_payment_charge_id}")

    await message.answer(f"Оплата прошла успешно!", reply_markup=get_back_to_main())

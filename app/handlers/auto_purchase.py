from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.crud.auto_purchase import get_user_settings, update_settings
from app.keyboards.auto_purchase_kb import (
    get_auto_purchase_settings,
    get_price_buttons,
    get_supply_limit_buttons,
    get_cycles_buttons,
)

from app.keyboards.callback import AutoPurchaseSettingsCallback

router = Router()


@router.callback_query(AutoPurchaseSettingsCallback.filter())
async def show_auto_purchase_settings(callback: CallbackQuery, callback_data: AutoPurchaseSettingsCallback):
    """Показать настройки автопокупки"""

    if callback_data.type == "min_price":
        await update_settings(callback.from_user.id, min_price=callback_data.number)
    elif callback_data.type == "max_price":
        await update_settings(callback.from_user.id, max_price=callback_data.number)
    elif callback_data.type == "supply_limit":
        await update_settings(callback.from_user.id, supply_limit=callback_data.number)
    elif callback_data.type == "cycles":
        await update_settings(callback.from_user.id, purchase_cycles=callback_data.number)
    elif callback_data.type == "is_enabled":
        await update_settings(callback.from_user.id, is_enabled=callback_data.number)

    settings = await get_user_settings(callback.from_user.id)
    
    await callback.message.edit_text(
        "⚙️ Настройки автопокупки\n\n"
        f"Статус: {'🟢 Включено' if settings.is_enabled else '🔴 Выключено'}\n\n"
        "Лимит цены:\n"
        f"От {settings.min_price} до {settings.max_price} ⭐️\n\n"
        f"Лимит саплая: {settings.supply_limit}\n\n"
        f"Количество циклов: {settings.purchase_cycles}",
        reply_markup=get_auto_purchase_settings(is_auto_purchase=settings.is_enabled)
    )

@router.callback_query(F.data == "min_price")
async def show_min_price_settings(callback: CallbackQuery):
    """Показать настройки минимальной цены"""
    await callback.message.edit_text(
        "Выбери новый минимум цены для автопокупки:\n(бот не отправит подарок дешевле установленного лимита)",
        reply_markup=get_price_buttons(type="min_price")
    )
    

@router.callback_query(F.data == "max_price")
async def show_max_price_settings(callback: CallbackQuery):
    """Показать настройки максимальной цены"""
    await callback.message.edit_text(
        "Выбери новый максимум цены для автопокупки:\n(бот не отправит подарок дороже установленного лимита)",
        reply_markup=get_price_buttons(type="max_price")
    )

@router.callback_query(F.data == "supply_limit")
async def show_supply_limit_settings(callback: CallbackQuery):
    """Показать настройки лимита саплая"""
    await callback.message.edit_text(
        "Выбери новый лимит саплая для автопокупки:\n(бот не отправит подарок, если их выпущено больше установленного лимита)",
        reply_markup=get_supply_limit_buttons()
    )

@router.callback_query(F.data == "cycles")
async def show_cycles_settings(callback: CallbackQuery):
    """Показать настройки количества циклов"""
    await callback.message.edit_text(
        "Выбери новое количество циклов автопокупки:\n(то, сколько раз бот купит новый подарок, например: выходит 3 подарка, циклов 2 - бот купит каждый по 2 раза = 6 подарков)",
        reply_markup=get_cycles_buttons()
    )
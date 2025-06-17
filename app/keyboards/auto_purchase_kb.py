from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboards.callback import AutoPurchaseSettingsCallback


def get_auto_purchase_settings(is_auto_purchase: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_auto_purchase:    
        builder.button(text="Выключить", callback_data=AutoPurchaseSettingsCallback(number=False, type="is_enabled"))
    else:
        builder.button(text="Включить", callback_data=AutoPurchaseSettingsCallback(number=True, type="is_enabled"))

    builder.button(text="Лимит цены от", callback_data="min_price")
    builder.button(text="Лимит цены до", callback_data="max_price")
    builder.button(text="Лимит саплая", callback_data="supply_limit")
    builder.button(text="Циклы автопокупки", callback_data="cycles")
    builder.add(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
    builder.adjust(1, 2, 1, 1, 1)
    return builder.as_markup()

def get_price_buttons(type: str) -> InlineKeyboardMarkup:
    prices = [15, 25, 50, 100, 200, 500, 1000, 2000, 2500, 3000, 5000, 10000, 20000]
    builder = InlineKeyboardBuilder()
    for price in prices:
        builder.button(text=str(price), callback_data=AutoPurchaseSettingsCallback(number=price, type=type))
    builder.button(text="Убрать лимит", callback_data=AutoPurchaseSettingsCallback(number=0, type=type))
    builder.button(text="Назад", callback_data=AutoPurchaseSettingsCallback(number=0, type="open_settings"))
    builder.adjust(2)
    return builder.as_markup()

def get_supply_limit_buttons() -> InlineKeyboardMarkup:
    limits = [500, 1000, 1500, 2000, 3000, 5000, 7500, 10000, 10000, 15000, 25000, 50000, 100000, 250000]
    builder = InlineKeyboardBuilder()
    for limit in limits:
        builder.button(text=str(limit), callback_data=AutoPurchaseSettingsCallback(number=limit, type="supply_limit"))
    builder.button(text="Убрать лимит", callback_data=AutoPurchaseSettingsCallback(number=0, type="supply_limit"))
    builder.button(text="Назад", callback_data=AutoPurchaseSettingsCallback(number=0, type="open_settings"))
    builder.adjust(2)
    return builder.as_markup()

def get_cycles_buttons() -> InlineKeyboardMarkup:
    cycles = [1, 2, 3, 5, 10, 20, 30, 50, 75, 100, 150, 200, 300]
    builder = InlineKeyboardBuilder()
    for cycle in cycles:
        builder.button(text=str(cycle), callback_data=AutoPurchaseSettingsCallback(number=cycle, type="cycles"))
    builder.button(text="Назад", callback_data=AutoPurchaseSettingsCallback(number=0, type="open_settings"))
    builder.adjust(2)
    return builder.as_markup() 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.callback import AutoPurchaseSettingsCallback

def get_main_menu() -> InlineKeyboardMarkup:
    """Получить клавиатуру главного меню"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Пополнить баланс", callback_data="deposit")
    builder.button(text="⚙️ Настройки", callback_data=AutoPurchaseSettingsCallback(number=0, type="open_settings"))
    builder.adjust(1)
    return builder.as_markup()

# def get_back_to_main() -> InlineKeyboardMarkup:
#     """Получить клавиатуру с кнопкой возврата в главное меню"""
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")
#             ]
#         ]
#     ) 
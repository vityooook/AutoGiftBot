from aiogram.filters.callback_data import CallbackData


class AutoPurchaseSettingsCallback(CallbackData, prefix="auto_settings"):
    type: str
    number: int

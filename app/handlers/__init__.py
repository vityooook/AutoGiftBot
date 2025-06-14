from aiogram import Router

from app.handlers.start import router as start_router
from app.handlers.deposit import router as deposit_router
from app.handlers.refund import router as refund_router
from app.handlers.auto_purchase import router as auto_purchase_router
from app.handlers.admin import router as admin_router
from app.handlers.test import router as test_router

def register_all_handlers(router: Router) -> None:
    """Регистрация всех обработчиков"""
    router.include_router(start_router)
    router.include_router(deposit_router)
    router.include_router(refund_router)
    router.include_router(auto_purchase_router)
    router.include_router(admin_router)
    router.include_router(test_router)
    
def get_handlers_router() -> Router:
    """Получение основного роутера с зарегистрированными обработчиками"""
    router = Router()
    register_all_handlers(router)
    return router 
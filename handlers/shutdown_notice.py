from aiogram import Router, types

router = Router()

SHUTDOWN_MESSAGE = (
    "⚠ Бот завершил свою работу и больше не доступен для использования.\n"
    "Спасибо всем, кто им пользовался 🙏"
)

# Перехватываем ТОЛЬКО callback'и (нажатия на кнопки)
@router.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    try:
        await callback.answer()  # убираем индикатор загрузки
    except:
        pass
    await callback.message.answer(SHUTDOWN_MESSAGE)

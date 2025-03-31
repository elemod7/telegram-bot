from aiogram import Router, types
from aiogram.filters import Command
from shared import access_manager, bot_instance, main_menu_keyboard, admin_only

router = Router()

@router.message()
async def debug_all_messages(message: types.Message):
    print(f"[DEBUG] Необработанное сообщение: {message.text} от {message.from_user.id}")
    await message.answer("Команда не распознана. Воспользуйся меню или напиши /start.")

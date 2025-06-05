import os
import asyncio
from aiogram import Router, types
from aiogram.types import FSInputFile
from shared import access_required, db
from menu import MENU_STRUCTURE, CONTENT, PDF_FILES, generate_menu

router = Router()

@router.callback_query()
@access_required
async def handle_menu_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.full_name
    callback_data = callback.data

    button_text = None
    for section in MENU_STRUCTURE.values():
        for text, value in section.items():
            if value == callback_data:
                button_text = text
                break
        if button_text:
            break

    action = f"Нажал кнопку: {button_text or callback_data}"
    await db.log_action(user_id, username, action)

    if callback_data in MENU_STRUCTURE:
        try:
            await callback.message.edit_text("Выбери раздел:", reply_markup=generate_menu(callback_data))
        except Exception:
            await callback.message.answer("Выбери раздел:", reply_markup=generate_menu(callback_data))
        return

    if callback_data in CONTENT:
        await callback.message.answer(CONTENT[callback_data], parse_mode="Markdown")
        return

    if callback_data in PDF_FILES:
        file_path = PDF_FILES[callback_data]
        await callback.answer()
        try:
            sending_message = await callback.bot.send_message(user_id, 
                "📂 Файл отправляется... Пожалуйста, подождите ⏳")
        except Exception as e:
            print(f"Ошибка при отправке уведомления: {e}")
            sending_message = None

        try:
            if os.path.exists(file_path):
                await callback.bot.send_document(user_id, FSInputFile(file_path))
            else:
                await callback.bot.send_message(user_id, 
                    "⚠️ В продукте поменялись условия, новая презентация будет доступна в ближайшее время.")
        except Exception as e:
            await callback.bot.send_message(user_id, f"❌ Ошибка при отправке файла: {e}")
        finally:
            if sending_message:
                try:
                    await sending_message.delete()
                except Exception as e:
                    print(f"Ошибка при удалении уведомления: {e}")
        return

    try:
        await callback.answer("Неизвестное действие.", show_alert=True)
    except Exception:
        pass

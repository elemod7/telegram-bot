import os
import asyncio
from aiogram import Router, types
from aiogram.types import FSInputFile
from menu import MENU_STRUCTURE, CONTENT, PDF_FILES, generate_menu
from shared import access_required, db

router = Router()

@router.callback_query()
@access_required
async def handle_menu_callbacks(callback_query: types.CallbackQuery):
    menu_key = callback_query.data
    user_id = callback_query.from_user.id
    username = callback_query.from_user.full_name

    button_text = None
    for menu_section in MENU_STRUCTURE.values():
        for key, value in menu_section.items():
            if value == menu_key:
                button_text = key
                break
        if button_text:
            break

    action_text = f"Нажал кнопку: {button_text}" if button_text else f"Выбрал {menu_key}"
    await db.log_action(user_id, username, action_text)

    if menu_key in CONTENT:
        await callback_query.message.answer(CONTENT[menu_key], parse_mode="Markdown")
        return

    if menu_key in MENU_STRUCTURE:
        try:
            await callback_query.message.edit_text("Выбери раздел:", reply_markup=generate_menu(menu_key))
        except Exception:
            await callback_query.message.answer("Выбери раздел:", reply_markup=generate_menu(menu_key))
        return

    if menu_key in PDF_FILES:
        file_path = PDF_FILES[menu_key]
        await callback_query.answer()
        try:
            sending_message = await callback_query.bot.send_message(user_id, 
                "📂 Файл отправляется... Пожалуйста, подождите ⏳")
        except Exception as e:
            print(f"Ошибка при отправке уведомления: {e}")
            sending_message = None

        try:
            if os.path.exists(file_path):
                await callback_query.bot.send_document(user_id, FSInputFile(file_path))
            else:
                await callback_query.bot.send_message(user_id, 
                    "⚠️ Этот файл пока недоступен. Он появится в ближайшее время.")
        except Exception as e:
            await callback_query.bot.send_message(user_id, f"❌ Ошибка при отправке файла: {e}")
        finally:
            if sending_message:
                try:
                    await sending_message.delete()
                except Exception as e:
                    print(f"Ошибка при удалении уведомления: {e}")
        return

    try:
        await callback_query.answer("Действие не распознано.", show_alert=True)
    except Exception:
        pass

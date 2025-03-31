from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from shared import admin_only, main_menu_keyboard, content_manager
from menu import CONTENT

router = Router()

class EditContent(StatesGroup):
    waiting_for_section = State()
    waiting_for_new_content = State()

@router.callback_query(lambda c: c.data.startswith("edit_"))
@admin_only
async def edit_section(callback_query: types.CallbackQuery, state: FSMContext):
    section = callback_query.data[5:]
    await state.update_data(section=section)
    current_content = CONTENT.get(section, "Пусто")
    await callback_query.message.answer(f"Редактирование: {section}\nТекущий контент:\n{current_content}\nВведите новый текст.")
    await state.set_state(EditContent.waiting_for_new_content)

@router.message(EditContent.waiting_for_new_content)
@admin_only
async def save_new_content(message: types.Message, state: FSMContext):
    data = await state.get_data()
    section = data.get("section")
    CONTENT[section] = message.text

    content_manager.save_content(CONTENT)

    await message.answer(f"Контент обновлён: {section}", reply_markup=main_menu_keyboard)
    await state.clear()

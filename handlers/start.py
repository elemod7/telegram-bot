from aiogram import Router, types
from aiogram.filters import Command
from shared import access_required, db, main_menu_keyboard 
from menu import generate_menu

router = Router()

async def show_main_menu(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.full_name

    await db.log_action(user_id, username, "Открыл главное меню")

    await message.answer(
        "Привет! Добро пожаловать в пространство возможностей и роста! 🔥\n\n"
        "Здесь ты найдёшь всё, что поможет тебе стать лидером: "
        "актуальные презентации, техники продаж, мотивацию за сделки, условия наших конкурсов и многое другое. "
        "Каждый день — это шанс добиться большего! 🚀",
        reply_markup=main_menu_keyboard 
    )

    # Inline-меню
    await message.answer(
        "С чего начнём сегодня? 😉",
        reply_markup=generate_menu("Главное меню")
    )


@router.message(Command("start"))
@access_required
async def main_menu(message: types.Message):
    await show_main_menu(message)


@router.message(lambda message: message.text == "На главную")
@access_required
async def return_to_main_menu(message: types.Message):
    await show_main_menu(message)

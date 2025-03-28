import shared
import asyncio
from shared import access_manager, ADMIN_ID, bot_instance, admin_only
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shared import access_manager, main_menu_keyboard, ADMIN_ID, db
from menu import generate_menu

router = Router()

def build_approve_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Предоставить доступ", callback_data=f"approve_{user_id}")]]
    )


async def handle_access_request(user_id: int, username: str, message_func):
    if access_manager.check_access(user_id):
        await message_func("У вас уже есть доступ к боту!")
        return

    requests = access_manager.load_access_requests()
    if str(user_id) in requests:
        await message_func("Ваш запрос уже отправлен и ожидает подтверждения.")
        return

    access_manager.add_access_request(user_id, username)
    await message_func("Запрос на доступ отправлен администратору. Ожидайте подтверждения.")

    try:
        bot = shared.bot_instance
        approve_button = build_approve_keyboard(user_id)
        await bot.send_message(
            ADMIN_ID,
            f"📥 Пользователь {username} (ID: {user_id}) запросил доступ к боту.",
            reply_markup=approve_button
        )
        print(f"[ACCESS] Запрос от {username} отправлен админу")
    except Exception as e:
        print(f"[ERROR] Не удалось отправить сообщение админу: {e}")


@router.message(Command("request_access"))
async def request_access_command(message: types.Message):
    await handle_access_request(
        user_id=message.from_user.id,
        username=message.from_user.full_name,
        message_func=message.answer
    )


@router.callback_query(lambda c: c.data == "request_access")
async def inline_request_access(callback_query: types.CallbackQuery):
    await handle_access_request(
        user_id=callback_query.from_user.id,
        username=callback_query.from_user.full_name,
        message_func=lambda text: callback_query.message.edit_text(text)
    )


@router.callback_query(lambda c: c.data.startswith("approve_"))
async def approve_access(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])

    if access_manager.grant_access(user_id):
        await callback_query.message.edit_text(f"✅ Доступ предоставлен пользователю с ID: {user_id}")

        try:
            bot = shared.bot_instance
            await bot.send_message(
                chat_id=user_id,
                text="Ваш запрос на доступ был одобрен. Теперь вы можете использовать бота!"
            )
            
            await bot.send_message(
                chat_id=user_id,
                text=(
                    "Привет! Добро пожаловать в пространство возможностей и роста! 🔥\n\n"
                    "Здесь ты найдёшь всё, что поможет тебе стать лидером: "
                    "актуальные презентации, техники продаж, мотивацию за сделки и условия наших конкурсов. "
                    "Каждый день — это шанс добиться большего! 🚀"
                ),
                reply_markup=shared.main_menu_keyboard
            )

            from menu import generate_menu
            await bot.send_message(
                chat_id=user_id,
                text="С чего начнём сегодня? 😉",
                reply_markup=generate_menu("Главное меню")
            )
        except Exception as e:
            print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
    else:
        await callback_query.message.edit_text(f"Пользователь с ID: {user_id} уже имеет доступ.")

@router.message(Command("list_allowed_users"))
@admin_only
async def list_allowed_users(message: types.Message, **kwargs):
    allowed_users = access_manager.list_allowed_users()
    if not allowed_users:
        await message.answer("Список пользователей с доступом пуст.")
        return

    user_info_list = []
    for user_id, name in allowed_users.items():
        user_info_list.append(f"{name} (ID: {user_id})")
    users_list = "\n".join(user_info_list)
    await message.answer(f"Пользователи с доступом:\n{users_list}")


@router.message(Command("remove_access"))
@admin_only
async def remove_access(message: types.Message, **kwargs):
    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.answer("Использование команды: /remove_access [ID пользователя]")
        return

    try:
        user_id = int(command_parts[1])
    except ValueError:
        await message.answer("ID пользователя должен быть числом.")
        return

    if access_manager.remove_access(user_id):
        await message.answer(f"Доступ удалён для пользователя с ID: {user_id}")
        try:
            await bot_instance.send_message(
                user_id,
                "Ваш доступ к боту был отозван. Для повторного запроса доступа воспользуйтесь командой /request_access."
            )
            await bot_instance.send_message(
                user_id,
                "Привет! Добро пожаловать в пространство возможностей и роста! 🔥\n\n"
                "Чтобы снова получить доступ, воспользуйтесь командой /request_access."
            )
        except Exception as e:
            print(f"Ошибка при уведомлении пользователя {user_id}: {e}")
    else:
        await message.answer(f"Пользователь с ID: {user_id} не найден в списке разрешённых.")

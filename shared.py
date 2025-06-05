import os
from dotenv import load_dotenv
from aiogram import Bot
from database import DatabaseManager
from access_management import AccessManager
from functools import wraps
from aiogram import types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot_instance: Bot = None
db = DatabaseManager()

access_manager = AccessManager(
    allowed_users_file="allowed_users.json",
    access_requests_file="access_requests.json"
)

# ✅ Только одна Reply‑кнопка под полем ввода — "На главную"
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="На главную")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# === Декораторы доступа ===

def access_required(handler):
    @wraps(handler)
    async def wrapper(event: types.Message | types.CallbackQuery, *args, **kwargs):
        user_id = event.from_user.id

        if not access_manager.check_access(user_id):
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Запросить доступ", callback_data="request_access")]]
            )

            if isinstance(event, types.Message):
                await event.answer(
                    "👋 Привет! Похоже, у тебя ещё нет доступа к этому боту. Нажми на кнопку ниже, чтобы запросить его у администратора.",
                    reply_markup=keyboard
                )
            else:
                await event.answer(
                    "👋 Привет! Похоже, у тебя ещё нет доступа к этому боту.",
                    show_alert=True
                )
                await event.message.edit_reply_markup(reply_markup=keyboard)

            return

        return await handler(event, *args, **kwargs)

    return wrapper


def admin_only(handler):
    @wraps(handler)
    async def wrapper(event: types.Message | types.CallbackQuery, *args, **kwargs):
        user_id = event.from_user.id

        if user_id != ADMIN_ID:
            if isinstance(event, types.Message):
                await event.answer("🚫 Эта команда доступна только администратору.")
            elif isinstance(event, types.CallbackQuery):
                await event.answer("🚫 Только для администратора.", show_alert=True)
            return

        return await handler(event, *args, **kwargs)

    return wrapper

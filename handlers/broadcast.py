from aiogram import Router, types, F
from aiogram.filters import Command
import json
import asyncio
from shared import ADMIN_ID

router = Router()

# Храним текст рассылки перед подтверждением
broadcast_messages = {}

@router.message(Command(commands=["broadcast"]))
async def start_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У тебя нет прав для этой команды.")
        return

    await message.answer("Отправь мне текст для рассылки:")
    broadcast_messages[message.from_user.id] = None

@router.message(lambda message: message.from_user.id == ADMIN_ID and broadcast_messages.get(message.from_user.id) is None)
async def get_broadcast_text(message: types.Message):
    broadcast_messages[message.from_user.id] = message.text
    await message.answer(f"Подтверди отправку рассылки:\n\n{message.text}\n\nНапиши 'Да' для подтверждения или 'Нет' для отмены.")

@router.message(lambda message: message.from_user.id == ADMIN_ID and broadcast_messages.get(message.from_user.id) is not None)
async def confirm_broadcast(message: types.Message):
    user_id = message.from_user.id

    if message.text.lower() == "да":
        try:
            with open("allowed_users.json", "r", encoding="utf-8") as f:
                allowed_users = json.load(f)
        except Exception as e:
            await message.answer(f"Ошибка при загрузке списка пользователей: {e}")
            return

        text_to_send = broadcast_messages[user_id]
        success, fail = 0, 0

        for chat_id in allowed_users.keys():
            try:
                await message.bot.send_message(chat_id, text_to_send)
                await asyncio.sleep(0.2)
                success += 1
            except Exception as e:
                print(f"Ошибка при отправке {chat_id}: {e}")
                fail += 1

        await message.answer(f"Рассылка завершена: ✅ {success} / ❌ {fail}")
        broadcast_messages[user_id] = None

    elif message.text.lower() == "нет":
        await message.answer("Рассылка отменена.")
        broadcast_messages[user_id] = None
    else:
        await message.answer("Напиши 'Да' или 'Нет' для подтверждения.")

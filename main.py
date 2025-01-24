import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers import register_handlers

load_dotenv()
API_TOKEN = os.getenv("BOT_API_TOKEN")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add(KeyboardButton("Вернуться на главную"))

register_handlers(dp, main_menu_keyboard)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

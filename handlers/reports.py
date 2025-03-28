from aiogram import Router, types
from aiogram.filters import Command
import shared 
from shared import db, admin_only
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(Command("report"))
@admin_only
async def generate_report(message: types.Message):
    """Генерация отчёта для администратора."""
    try:
        report_data = await db.generate_daily_report()
        if not report_data:
            await message.answer("📊 Отчёт пуст: сегодня нет активности.")
            return

        await message.answer(
            f"📊 Отчёт за сегодня:\n\n{report_data}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка при генерации отчёта: {e}")

@router.message(Command("clear_logs"))
@admin_only
async def clear_logs(message: types.Message):
    """Очистка базы данных логов (только для администратора)."""
    try:
        await db.clear_logs()
        await message.answer("✅ Логи успешно очищены.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при очистке логов: {e}")

@router.message(Command("send_report"))
@admin_only
async def send_report_to_admin(message: types.Message):
    """Принудительная отправка отчёта админу."""
    try:
        report_data = await db.generate_daily_report()
        if not report_data:
            await message.answer("📊 Отчёт пуст: сегодня нет активности.")
            return

        await shared.bot_instance.send_message(
            shared.ADMIN_ID, 
            f"📊 Принудительный отчёт:\n\n{report_data}",
            parse_mode="Markdown"
        )
        await message.answer("📤 Отчёт отправлен админу.")

    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке отчёта: {e}")

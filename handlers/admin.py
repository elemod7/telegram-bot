from aiogram import Router, types
from aiogram.filters import Command
from shared import bot_instance, admin_only

router = Router()

@router.message(Command("admin"))
@admin_only
async def admin_panel(message: types.Message):
    print(f"DEBUG: {message.from_user.id} открыл админ-панель.")

    admin_commands = (
        "🔧 *Админ\\-команды:*\n\n"
        "/report \\- Отчёт о действиях пользователей\n"
        "/clear\\_logs \\- Очистка базы данных отчётов\n\n"
        
        "🔐 *Управление доступом:*\n"
        "/request\\_access \\- Запросить доступ\n"
        "/grant\\_access \\[ID\\] \\- Дать доступ пользователю\n"
        "/remove\\_access \\[ID\\] \\- Удалить доступ у пользователя\n"
        "/list\\_allowed\\_users \\- Список пользователей с доступом\n\n"
        
        "✍️ *Редактирование контента:*\n"
        "/edit\\_\\[раздел\\] \\- Редактировать текст раздела\n\n"
        
        "✅ *Дополнительное:*\n"
        "На главную \\- Вернуться в главное меню"
    )

    await message.answer(admin_commands, parse_mode="MarkdownV2")

@router.message(Command("clear_logs"))
@admin_only
async def clear_logs_command(message: types.Message):
    """Команда для очистки логов администратором"""
    from shared import db 
    
    if await db.clear_logs():
        await message.answer("✅ Логи успешно очищены!")
    else:
        await message.answer("❌ Ошибка при очистке логов. Проверь консоль.")

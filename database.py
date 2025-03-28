import aiosqlite
import datetime
import pytz

DB_FILE = "bot_usage.db"
MOSCOW_TZ = pytz.timezone("Europe/Moscow")


class DatabaseManager:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file

    async def initialize_db(self):
        """Инициализация базы данных (создание таблицы, если не существует)."""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def log_action(self, user_id, username, action):
        """Логирование действий пользователей."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                "INSERT INTO user_actions (user_id, username, action, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, username, action, timestamp)
            )
            await db.commit()

    async def generate_daily_report(self):
        """Генерация отчёта за текущий день."""
        today_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute("""
                SELECT username, user_id, action, timestamp 
                FROM user_actions
                WHERE date(timestamp) = ?
                ORDER BY user_id, timestamp ASC
            """, (today_utc,))
            rows = await cursor.fetchall()

        if not rows:
            return "📊 Отчёт за сегодня: нет активности."

        report_data = {}

        for username, user_id, action, timestamp in rows:
            try:
                dt_object = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
                moscow_time = dt_object.astimezone(MOSCOW_TZ)

                date_str = moscow_time.strftime("%Y-%m-%d")
                time_str = moscow_time.strftime("%H:%M:%S")

                user_key = f"{username} (ID: {user_id})"
                if user_key not in report_data:
                    report_data[user_key] = []

                report_data[user_key].append(f"{date_str} {time_str} - {action}")

            except Exception as e:
                print(f"[ERROR] Ошибка обработки timestamp ({timestamp}): {e}")
                continue  

        report_lines = ["📊 *Отчёт за сегодня:*"]
        for user, actions in report_data.items():
            report_lines.append(user)
            report_lines.extend(actions)
            report_lines.append("")

        return "\n".join(report_lines)

    async def clear_logs(self):
        """Очистка логов действий пользователей."""
        async with aiosqlite.connect(self.db_file) as db:
            try:
                await db.execute("DELETE FROM user_actions")
                await db.commit()
                return True
            except Exception as e:
                print(f"[ERROR] Ошибка при очистке логов: {e}")
                return False

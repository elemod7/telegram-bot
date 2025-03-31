#!/bin/bash

echo "🚨 ВНИМАНИЕ! Сейчас будет удалена вся история Git и произведён пуш заново."
read -p "Продолжить? (y/N): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "❌ Отменено."
  exit 1
fi

# Удаляем старую историю
echo "🧹 Удаляем .git..."
rm -rf .git

# Инициализируем репозиторий заново
echo "🔧 Инициализируем новый git-репозиторий..."
git init
git checkout -b main

# Добавляем все файлы
git add .

# Коммит
git commit -m "🔥 Полная перезаливка проекта"

# Привязка к GitHub
git remote add origin https://github.com/elemod7/telegram-bot.git

# Пуш с перезаписью
echo "🚀 Заливаем на GitHub с --force..."
git push origin main --force

echo "✅ Готово! Репозиторий перезалит."

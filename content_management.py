import json
import os

class ContentManager:
    def __init__(self, content_file):
        self.content_file = content_file

    def load_content(self):
        if not os.path.exists(self.content_file):
            return {}
        try:
            with open(self.content_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Ошибка: файл {self.content_file} поврежден.")
            return {}

    def save_content(self, content):
        try:
            with open(self.content_file, "w", encoding="utf-8") as file:
                json.dump(content, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения контента в {self.content_file}: {e}")

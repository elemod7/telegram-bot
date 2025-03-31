import json
import os

class AccessManager:
    def __init__(self, allowed_users_file, access_requests_file):
        self.allowed_users_file = allowed_users_file
        self.access_requests_file = access_requests_file

    def load_allowed_users(self):
        try:
            with open(self.allowed_users_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    data = {str(user_id): str(user_id) for user_id in data}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_allowed_users(self, users):
        with open(self.allowed_users_file, "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)

    def check_access(self, user_id):
        return str(user_id) in self.load_allowed_users()

    def add_access_request(self, user_id, name):
        requests = self.load_access_requests()
        requests[str(user_id)] = {"name": name, "id": user_id}
        self.save_access_requests(requests)

    def load_access_requests(self):
        try:
            with open(self.access_requests_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_access_requests(self, requests):
        with open(self.access_requests_file, "w", encoding="utf-8") as file:
            json.dump(requests, file, ensure_ascii=False, indent=4)

    def grant_access(self, user_id):
        requests = self.load_access_requests()
        if str(user_id) in requests:
            allowed_users = self.load_allowed_users()
            allowed_users[str(user_id)] = requests[str(user_id)]["name"]
            self.save_allowed_users(allowed_users)
            del requests[str(user_id)]
            self.save_access_requests(requests)
            return True
        return False

    def list_access_requests(self):
        return self.load_access_requests().values()

    def list_allowed_users(self):
        return self.load_allowed_users()

    def remove_access(self, user_id):
        allowed_users = self.load_allowed_users()
        if str(user_id) in allowed_users:
            del allowed_users[str(user_id)]
            self.save_allowed_users(allowed_users)
            return True
        return False

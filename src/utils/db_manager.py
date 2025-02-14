import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import shutil
import numpy as np

class DBManager:
    def __init__(self, db_file: str, images_dir: str):
        self.db_file = db_file
        self.images_dir = images_dir
        self._ensure_directories()
        self.users_db = self._load_database()

    def _ensure_directories(self) -> None:
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        db_dir = os.path.dirname(self.db_file)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _load_database(self) -> Dict[str, Any]:
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading database file: {self.db_file}")
                return {}
        return {}

    def save_database(self) -> bool:
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.users_db, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False

    def user_exists(self, username: str) -> bool:
        return username in self.users_db

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        return self.users_db.get(username)

    def save_user(self, username: str, face_encoding: np.ndarray,
                  original_image_path: str) -> bool:
        try:
            saved_image_path = self._save_user_image(original_image_path, username)
            if not saved_image_path:
                return False

            self.users_db[username] = {
                'face_encoding': face_encoding.tolist() if face_encoding is not None else None,
                'image_path': saved_image_path,
                'created_at': datetime.now().isoformat()
            }

            return self.save_database()
        except Exception as e:
            print(f"Error saving user: {e}")
            return False

    def _save_user_image(self, original_path: str, username: str) -> Optional[str]:
        try:
            extension = os.path.splitext(original_path)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{username}_{timestamp}{extension}"
            new_path = os.path.join(self.images_dir, new_filename)

            shutil.copy2(original_path, new_path)
            return new_path
        except Exception as e:
            print(f"Error saving user image: {e}")
            return None

    def update_user(self, username: str, data: Dict[str, Any]) -> bool:
        if username not in self.users_db:
            return False

        try:
            self.users_db[username].update(data)
            return self.save_database()
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def delete_user(self, username: str) -> bool:
        if username not in self.users_db:
            return False

        try:
            image_path = self.users_db[username].get('image_path')
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

            del self.users_db[username]
            return self.save_database()
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def get_all_users(self) -> Dict[str, Any]:
        return self.users_db

    def backup_database(self, backup_path: str) -> bool:
        try:
            shutil.copy2(self.db_file, backup_path)

            images_backup_dir = os.path.join(
                os.path.dirname(backup_path),
                'images_backup'
            )
            if os.path.exists(images_backup_dir):
                shutil.rmtree(images_backup_dir)
            shutil.copytree(self.images_dir, images_backup_dir)

            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def verify_database_integrity(self) -> List[str]:
        errors = []

        for username, data in self.users_db.items():
            required_fields = ['password', 'face_encoding', 'image_path']
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing {field} for user {username}")

            image_path = data.get('image_path')
            if image_path and not os.path.exists(image_path):
                errors.append(f"Missing image file for user {username}")

        return errors
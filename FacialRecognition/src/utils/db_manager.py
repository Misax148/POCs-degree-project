import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import shutil
import numpy as np

class DBManager:
    def __init__(self, db_file: str, images_dir: str):
        """
        Initializes the database manager.

        Args:
            db_file (str): Path to the JSON database file
            images_dir (str): Directory path where user profile images will be stored
        """
        self.db_file = db_file
        self.images_dir = images_dir
        self._ensure_directories()
        self.users_db = self._load_database()

    def _ensure_directories(self) -> None:
        """
        Creates necessary directories for database and images if they don't exist.
        """
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        db_dir = os.path.dirname(self.db_file)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _load_database(self) -> Dict[str, Any]:
        """
        Loads the user database from JSON file.

        Returns:
            Dict[str, Any]: Dictionary containing user data, empty if file doesn't exist
                           or can't be read
        """
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
        """
        Saves a new user to the database.

        Args:
            username (str): Username of the new user
            face_encoding (np.ndarray): Facial encoding data
            original_image_path (str): Path to user's profile image
        """
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
        """
        Saves user's profile image to images directory.

        Args:
            original_path (str): Path to original image file
            username (str): Username to associate with image

        Returns:
            Optional[str]: Path where image was saved, None if save failed
        """
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

    def get_all_users(self) -> Dict[str, Any]:
        return self.users_db
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class WelcomeFrame:
    def __init__(self, parent, db_manager, username):
        self.window = tk.Toplevel(parent)
        self.window.title("Welcome")

        ttk.Label(self.window, text=f"¡Welcome {username}!").pack(pady=10)

        user_data = db_manager.get_user(username)
        if user_data and "image_path" in user_data:
            image_path = user_data["image_path"]
            try:
                image = Image.open(image_path)
                image = image.resize((200, 200))
                photo = ImageTk.PhotoImage(image)
                img_label = ttk.Label(self.window, image=photo)
                img_label.image = photo
                img_label.pack(pady=10)
            except Exception as e:
                print(f"Error loading image: {e}")

        ttk.Button(
            self.window,
            text="Back",
            command=self.window.destroy
        ).pack(pady=10)
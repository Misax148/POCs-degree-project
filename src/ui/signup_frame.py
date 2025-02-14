import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from ..utils.db_manager import DBManager
from ..interfaces.face_recognizer import FaceRecognizer

class SignupFrame(ttk.Frame):
    def __init__(self, parent, recognizer: FaceRecognizer, db_manager: DBManager):
        super().__init__(parent)
        self.recognizer = recognizer
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        label_user = ttk.Label(self, text="Username:")
        label_user.pack()
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack()

        self.upload_btn = ttk.Button(self, text="Upload Photo",
                                   command=self.upload_image)
        self.upload_btn.pack()

        self.image_label = ttk.Label(self)
        self.image_label.pack()

        self.signup_btn = ttk.Button(self, text="Sign Up",
                                   command=self.register_user)
        self.signup_btn.pack()

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.current_image_path = file_path
            image = Image.open(file_path)
            image = image.resize((150, 150))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo

    def register_user(self):
        username = self.username_entry.get()

        if self.db_manager.user_exists(username):
            messagebox.showerror("Error", "User already exists")
            return

        face_encoding = self.recognizer.get_face_encoding(self.current_image_path)
        if face_encoding is None:
            messagebox.showerror("Error", "No face detected")
            return

        self.db_manager.save_user(username, face_encoding,
                                  self.current_image_path)
        messagebox.showinfo("Success", "User registered successfully")

        self.username_entry.delete(0, tk.END)
        self.image_label.configure(image="")
        delattr(self, "current_image_path")
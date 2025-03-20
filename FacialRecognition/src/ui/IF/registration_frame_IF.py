import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import numpy as np

from src.interfaces.face_recognizer import FaceRecognizer
from src.utils.db_manager import DBManager


class RegistrationFrameIF(ttk.Frame):
    """
    Frame for user registration using facial recognition with InsightFace.
    Allows uploading a photo and registering with a username.
    """

    def __init__(self, parent, recognizer: FaceRecognizer, db_manager: DBManager):
        super().__init__(parent)
        self.recognizer = recognizer
        self.db_manager = db_manager
        self.current_image_path = None
        self.setup_ui()

    def setup_ui(self):
        """Sets up the user interface elements."""
        # Username entry
        username_frame = ttk.Frame(self)
        username_frame.pack(fill='x', padx=20, pady=20)

        username_label = ttk.Label(username_frame, text="Nombre de Usuario:")
        username_label.pack(side=tk.LEFT, padx=5)

        self.username_entry = ttk.Entry(username_frame, width=30)
        self.username_entry.pack(side=tk.LEFT, padx=5, fill='x', expand=True)

        # Photo upload
        photo_frame = ttk.Frame(self)
        photo_frame.pack(fill='x', padx=20, pady=10)

        self.upload_btn = ttk.Button(photo_frame, text="Subir Foto",
                                     command=self.upload_image)
        self.upload_btn.pack(side=tk.LEFT, padx=5)

        self.photo_label = ttk.Label(photo_frame, text="No se ha seleccionado ninguna foto")
        self.photo_label.pack(side=tk.LEFT, padx=5)

        # Image preview
        self.image_frame = ttk.Frame(self)
        self.image_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(pady=10)

        # Register button
        self.register_btn = ttk.Button(self, text="Registrar Usuario",
                                       command=self.register_user)
        self.register_btn.pack(pady=20)

    def upload_image(self):
        """Handles image upload for registration."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.current_image_path = file_path
            self.photo_label.config(text=os.path.basename(file_path))

            # Show image preview
            image = Image.open(file_path)
            image = image.resize((200, 200))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo

    def register_user(self):
        """
        Processes user registration.
        Validates input, detects face, and saves user data to database.
        """
        username = self.username_entry.get().strip()

        if not username:
            messagebox.showerror("Error", "Por favor ingrese un nombre de usuario")
            return

        if not self.current_image_path:
            messagebox.showerror("Error", "Por favor suba una foto")
            return

        if self.db_manager.user_exists(username):
            messagebox.showerror("Error", "El usuario ya existe")
            return

        # Show processing message
        processing_window = tk.Toplevel(self)
        processing_window.title("Procesando")
        processing_window.geometry("300x100")
        processing_label = ttk.Label(processing_window, text="Procesando imagen...")
        processing_label.pack(padx=20, pady=20)
        processing_window.update()

        # Detect face in the image using InsightFace
        face_encoding = self.recognizer.get_face_encoding(self.current_image_path)

        processing_window.destroy()

        if face_encoding is None:
            messagebox.showerror("Error", "No se detecto ningun rostro en la imagen")
            return

        if not isinstance(face_encoding, np.ndarray):
            face_encoding = np.array(face_encoding)

        dimension_info = f"Codificacion facial: {len(face_encoding)} dimensiones (InsightFace)"

        # Save user to database
        success = self.db_manager.save_user(username, face_encoding, self.current_image_path)
        if success:
            messagebox.showinfo("Exito", f"Usuario registrado correctamente\n{dimension_info}")

            # Clear fields
            self.username_entry.delete(0, tk.END)
            self.photo_label.config(text="No se ha seleccionado ninguna foto")
            self.image_label.configure(image="")
            self.current_image_path = None
        else:
            messagebox.showerror("Error", "No se pudo registrar el usuario")
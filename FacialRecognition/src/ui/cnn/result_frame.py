import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ResultFrame:
    """
    Window displayed after successful authentication.
    Shows the user's image and authentication details.
    """

    def __init__(self, parent, db_manager, username, distance, threshold):
        self.window = tk.Toplevel(parent)
        self.window.title("Resultado de Verificacion")
        self.window.geometry("400x500")

        result_frame = ttk.Frame(self.window)
        result_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Display welcome message with confidence info
        confidence = max(0, min(100, (1 - distance / threshold) * 100))
        welcome_label = ttk.Label(result_frame,
                                  text=f"Bienvenido {username}!",
                                  font=("Arial", 16, "bold"))
        welcome_label.pack(pady=10)

        # Display match metrics
        metrics_frame = ttk.Frame(result_frame)
        metrics_frame.pack(pady=5, fill='x')

        metrics_text = (
            f"Confianza: {confidence:.2f}%\n"
            f"Distancia: {distance:.4f}\n"
            f"Umbral: {threshold}"
        )

        metrics_label = ttk.Label(metrics_frame,
                                  text=metrics_text,
                                  font=("Arial", 10))
        metrics_label.pack()

        # Display security level indicator
        security_frame = ttk.Frame(result_frame)
        security_frame.pack(pady=5, fill='x')

        if confidence > 95:
            security_text = "Nivel de seguridad: ALTO"
            security_color = "green"
        elif confidence > 85:
            security_text = "Nivel de seguridad: MEDIO"
            security_color = "orange"
        else:
            security_text = "Nivel de seguridad: BAJO"
            security_color = "red"

        print(security_text + " - " + security_color)

        # Display user's stored image
        user_data = db_manager.get_user(username)
        if user_data and "image_path" in user_data:
            image_path = user_data["image_path"]
            try:
                image = Image.open(image_path)
                image = image.resize((250, 250))
                photo = ImageTk.PhotoImage(image)
                img_label = ttk.Label(result_frame, image=photo)
                img_label.image = photo  # Keep a reference to prevent garbage collection
                img_label.pack(pady=20)
            except Exception as e:
                error_label = ttk.Label(result_frame,
                                        text=f"Error al cargar la imagen: {e}")
                error_label.pack(pady=10)

        # Close button
        close_btn = ttk.Button(result_frame, text="Cerrar",
                               command=self.window.destroy)
        close_btn.pack(pady=10)
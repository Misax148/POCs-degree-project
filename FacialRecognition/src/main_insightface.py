import os
from src.recognizers.insightface_recognizer import InsightFaceRecognizer
from src.ui.IF.facial_auth_app_IF import FacialAuthAppIF
from src.utils.db_manager import DBManager
from src import config


def create_directories():
    """
    Creates necessary directories for application data.
    """
    directories = [
        config.DATA_DIR,
        config.MODELS_DIR_IF,
        config.IMAGES_DIR_IF
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def main():
    """
    Main application entry point using InsightFace.
    """
    # Create necessary directories
    create_directories()

    # Initialize database manager
    db_manager = DBManager(config.DB_FILE_IF, config.IMAGES_DIR_IF)

    # Initialize IF recognizer
    try:
        import insightface
        models_path = os.path.join(os.path.expanduser("~"), ".insightface", "models")

        if not os.path.exists(models_path):
            os.makedirs(models_path, exist_ok=True)

        print(f"Usando directorio de modelos: {models_path}")

        recognizer = InsightFaceRecognizer(model_folder=models_path)

        if not recognizer.is_initialized:
            print("ERROR: No se pudo iniciar IF")
            return

        print("Running")

    except ImportError:
        print("ERROR: IF no esta instalado")
        return
    except Exception as e:
        print(f"ERROR: No se pudo inicializar el reconocedor facial: {e}")
        return

    app = FacialAuthAppIF(recognizer, db_manager)
    app.run()


if __name__ == "__main__":
    main()
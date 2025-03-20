import os
from src.ui.app import FacialAuthApp
from src.utils.db_manager import DBManager
from src.recognizers.dlib_recognizer import DlibRecognizer
from src.recognizers.face_recognition_lib_recognizer import FaceRecognitionLibRecognizer
from src import config
from src.recognizers.dlib_cnn_recognizer import DlibCnnRecognizer
from src.recognizers.hybrid_recognizer import HybridRecognizer
from src.ui.app import FacialAuthApp
from src.ui.cnn.app_cnn_dlib import FacialAuthAppCNN

def create_directories():
    """
    Creates necessary directories for application data.
    Ensures existence of data, models, and images directories.
    """
    directories = [
        config.DATA_DIR,
        config.MODELS_DIR,
        config.IMAGES_DIR
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def check_models():
    """
    Checks if required model files exist.
    """
    required_models = [
        (config.SHAPE_PREDICTOR_PATH, "shape_predictor_68_face_landmarks.dat"),
        (config.RECOGNITION_MODEL_PATH, "dlib_face_recognition_resnet_model_v1.dat"),
    ]

    missing_models = []
    for model_path, model_name in required_models:
        if not os.path.exists(model_path):
            missing_models.append(model_name)

    if missing_models:
        print("ERROR: Faltan los siguientes archivos de modelo:")
        for model_name in missing_models:
            print(f"  - {model_name}")
        return False

    return True

def main():
    """
    Main application.
    """
    create_directories()

    db_manager = DBManager(config.DB_FILE, config.IMAGES_DIR)

    try:
        recognizer = HybridRecognizer(
            config.SHAPE_PREDICTOR_PATH,
            config.RECOGNITION_MODEL_PATH
        )
        print("Reconocedor facial CNN inicializado correctamente")
    except Exception as e:
        print(f"ERROR: {e}")
        return

    app = FacialAuthAppCNN(recognizer, db_manager)
    app.run()


if __name__ == "__main__":
    main()

# -------------------------------------------------------------------------------------------------
'''
def create_directories():
    """
    Creates necessary directories for application data.
    Ensures existence of data, models, and images directories.
    """
    directories = [
        config.DATA_DIR,
        config.MODELS_DIR,
        config.IMAGES_DIR
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def main():
    """
    Main application.
    """
    create_directories()

    db_manager = DBManager(config.DB_FILE, config.IMAGES_DIR)


    recognizer = DlibRecognizer(
        config.SHAPE_PREDICTOR_PATH,
        config.RECOGNITION_MODEL_PATH
    )

    # Option 2: use face_recognition
    #recognizer = FaceRecognitionLibRecognizer()

    app = FacialAuthApp(recognizer, db_manager)
    app.run()


if __name__ == "__main__":
    main()
'''
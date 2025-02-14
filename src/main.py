import os
from src.ui.app import FacialAuthApp
from src.utils.db_manager import DBManager
from src.recognizers.dlib_recognizer import DlibRecognizer
from src.recognizers.face_recognition_lib_recognizer import FaceRecognitionLibRecognizer
from src import config


def create_directories():
    directories = [
        config.DATA_DIR,
        config.MODELS_DIR,
        config.IMAGES_DIR
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def main():
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
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.recognizers.hybrid_recognizer import HybridRecognizer
from src.utils.db_manager import DBManager
from src.api.dlib_api import DlibAPI
from src import config


def create_directories():
    """
    Creates necessary directories for application data.
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
    required_models = [
        (config.SHAPE_PREDICTOR_PATH, "shape_predictor_68_face_landmarks.dat"),
        (config.RECOGNITION_MODEL_PATH, "dlib_face_recognition_resnet_model_v1.dat"),
    ]

    missing_models = []
    for model_path, model_name in required_models:
        if not os.path.exists(model_path):
            missing_models.append(model_name)

    if missing_models:
        for model_name in missing_models:
            print(f"Missing  - {model_name}")
        return False

    return True


def main():
    """
    Main application entry point for DLIB API.
    """
    create_directories()

    if not check_models():
        print("Missing models")
        return None

    db_manager = DBManager(config.DB_FILE, config.IMAGES_DIR)

    app = FastAPI(
        title="DLIB Recognition API",
        description="API para reconocimiento facial usando DLIB",
        version="1.0.0"
    )

    app.mount("/images", StaticFiles(directory=config.IMAGES_DIR), name="images")

    @app.get("/api/image/{image_name}")
    async def get_image(image_name: str):
        image_path = os.path.join(config.IMAGES_DIR, image_name)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        return FileResponse(image_path)

    try:
        recognizer = HybridRecognizer(
            config.SHAPE_PREDICTOR_PATH,
            config.RECOGNITION_MODEL_PATH
        )

    except Exception as e:
        print(f"ERROR: {e}")
        return None

    # Initialize API with the app, recognizer and db_manager
    api = DlibAPI(app, recognizer, db_manager)

    # Add a simple root endpoint
    @app.get("/")
    def read_root():
        return {"message": "DLIB Recognition API", "status": "online"}

    return app


app = main()

if __name__ == "__main__":
    if app:
        print("API INIT")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("Error")
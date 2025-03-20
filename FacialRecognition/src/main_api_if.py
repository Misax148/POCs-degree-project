import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.recognizers.insightface_recognizer import InsightFaceRecognizer
from src.utils.db_manager import DBManager
from src.api.insight_face_api import InsightFaceAPI
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
    Main application entry point for IF API.
    """
    create_directories()

    db_manager = DBManager(config.DB_FILE_IF, config.IMAGES_DIR_IF)

    app = FastAPI(
        title="InsightFace Recognition API",
        description="API para reconocimiento facial usando InsightFace",
        version="1.0.0"
    )

    app.mount("/images", StaticFiles(directory=config.IMAGES_DIR_IF), name="images")

    @app.get("/api/image/{image_name}")
    async def get_image(image_name: str):
        image_path = os.path.join(config.IMAGES_DIR_IF, image_name)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        return FileResponse(image_path)

    try:
        import insightface
        print("IF installed correct")
        models_path = os.path.join(os.path.expanduser("~"), ".insightface", "models")

        # Ensure models directory exists
        if not os.path.exists(models_path):
            os.makedirs(models_path, exist_ok=True)

        print(f"Usando directorio de modelos: {models_path}")

        recognizer = InsightFaceRecognizer(model_folder=models_path)

        if not recognizer.is_initialized:
            print("ERROR: IF not init")
            return

    except ImportError:
        print("ERROR: IF is not insttaled")
        return
    except Exception as e:
        print(f"ERROR: {e}")
        return

    # Initialize API with the app, recognizer and db_manager
    api = InsightFaceAPI(app, recognizer, db_manager)

    # Add a simple root endpoint
    @app.get("/")
    def read_root():
        return {"message": "InsightFace Recognition API", "status": "online"}

    return app


app = main()

if __name__ == "__main__":
    if app:
        print("API init")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("Error")
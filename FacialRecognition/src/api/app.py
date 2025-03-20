from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import numpy as np
import os
from pathlib import Path
import tempfile

from ..recognizers.face_recognition_lib_recognizer import FaceRecognitionLibRecognizer
from ..utils.db_manager import DBManager
from .. import config

app = FastAPI(title="Facial Recognition API")
app.mount("/userimg", StaticFiles(directory="/home/axel/Documents/JALA-USB/proyecto-de-grado/Proyecto de Grado 1/pocs/poc-v2/POCs-degree-project/FacialRecognition/data/images"), name="userimg")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recognizer = FaceRecognitionLibRecognizer()
db_manager = DBManager(config.DB_FILE, config.IMAGES_DIR)


async def save_upload_file_temp(upload_file: UploadFile) -> str:
    try:
        suffix = Path(upload_file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await upload_file.read()
            temp_file.write(content)
            return temp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")


@app.post("/signup")
async def signup(username: str = Form(...), image: UploadFile = File(...)):
    try:
        if db_manager.user_exists(username):
            raise HTTPException(status_code=400, detail="Username already exists")

        temp_file_path = await save_upload_file_temp(image)
        face_encoding = recognizer.get_face_encoding(temp_file_path)

        if face_encoding is None:
            os.unlink(temp_file_path)
            raise HTTPException(status_code=400, detail="No face detected in image")

        success = db_manager.save_user(username, face_encoding, temp_file_path)
        os.unlink(temp_file_path)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save user")

        return {"message": "User registered successfully", "username": username}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
async def login(image: UploadFile = File(...)):
    try:
        temp_file_path = await save_upload_file_temp(image)
        face_encoding = recognizer.get_face_encoding(temp_file_path)

        if face_encoding is None:
            os.unlink(temp_file_path)
            raise HTTPException(status_code=400, detail="No face detected in image")

        users = db_manager.get_all_users()

        for username, user_data in users.items():
            known_encoding = np.array(user_data['face_encoding'])
            if recognizer.compare_faces(known_encoding, face_encoding):
                os.unlink(temp_file_path)

                image_filename = os.path.basename(user_data['image_path'])
                return {
                    "message": "Authentication successful",
                    "username": username,
                    "image_url": f"/userimg/{image_filename}"
                }

        os.unlink(temp_file_path)
        raise HTTPException(status_code=401, detail="Face not recognized")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
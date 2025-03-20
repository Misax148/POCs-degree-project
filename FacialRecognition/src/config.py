import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(DATA_DIR, "models")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
DB_FILE = os.path.join(DATA_DIR, "users_db.json")

# Models
SHAPE_PREDICTOR_PATH = os.path.join(MODELS_DIR, "shape_predictor_68_face_landmarks.dat")
RECOGNITION_MODEL_PATH = os.path.join(MODELS_DIR, "dlib_face_recognition_resnet_model_v1.dat")
CNN_DETECTOR_PATH = os.path.join(MODELS_DIR, "mmod_human_face_detector.dat")

# IF paths
MODELS_DIR_IF = os.path.join(DATA_DIR, "models_IF")
IMAGES_DIR_IF = os.path.join(DATA_DIR, "images_IF")
DB_FILE_IF = os.path.join(DATA_DIR, "users_db_IF.json")
# dlib_recognizer.py
import dlib
import cv2
import numpy as np
from typing import Optional, Tuple, List
from ..interfaces.face_recognizer import FaceRecognizer


class DlibRecognizer(FaceRecognizer):
    def __init__(self, predictor_path: str, recognition_model_path: str):
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor(predictor_path)
        self.face_encoder = dlib.face_recognition_model_v1(recognition_model_path)

    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        if isinstance(image, str):
            image = cv2.imread(image)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        faces = self.face_detector(rgb_image)
        if not faces:
            return None

        shape = self.shape_predictor(rgb_image, faces[0])
        face_descriptor = self.face_encoder.compute_face_descriptor(rgb_image, shape)

        return np.array(face_descriptor)

    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.face_detector(rgb_frame)
        return [(face.top(), face.right(), face.bottom(), face.left())
                for face in faces]

    def compare_faces(self, known_encoding: np.ndarray,
                      face_encoding_to_check: np.ndarray,
                      tolerance: float = 0.6) -> bool:
        if isinstance(known_encoding, list):
            known_encoding = np.array(known_encoding)
        return np.linalg.norm(known_encoding - face_encoding_to_check) <= tolerance
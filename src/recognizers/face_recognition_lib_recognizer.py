import face_recognition
import numpy as np
from typing import Optional, Tuple, List
from ..interfaces.face_recognizer import FaceRecognizer


class FaceRecognitionLibRecognizer(FaceRecognizer):
    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        if isinstance(image, str):
            image = face_recognition.load_image_file(image)

        face_encodings = face_recognition.face_encodings(image)
        return face_encodings[0] if face_encodings else None

    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        return face_recognition.face_locations(frame)

    def compare_faces(self, known_encoding: np.ndarray,
                      face_encoding_to_check: np.ndarray,
                      tolerance: float = 0.6) -> bool:
        return face_recognition.compare_faces(
            [known_encoding], face_encoding_to_check, tolerance)[0]
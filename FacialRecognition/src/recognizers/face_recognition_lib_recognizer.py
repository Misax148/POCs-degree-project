import face_recognition
import numpy as np
from typing import Optional, Tuple, List
from ..interfaces.face_recognizer import FaceRecognizer


class FaceRecognitionLibRecognizer(FaceRecognizer):
    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        """
        Generates face encoding using face_recognition library.

        Args:
            image: Path to image file (str) or numpy array with image data
        """
        if isinstance(image, str):
            image = face_recognition.load_image_file(image)

        face_encodings = face_recognition.face_encodings(image)
        return face_encodings[0] if face_encodings else None

    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces using face_recognition library's HOG-based detector.

        Args:
            frame (np.ndarray): Image frame to detect faces in
        """
        return face_recognition.face_locations(frame)

    def compare_faces(self, known_encoding: np.ndarray,
                      face_encoding_to_check: np.ndarray,
                      tolerance: float = 0.6) -> bool:
        """
        Compares faces using face_recognition library's comparison function.

        Args:
            known_encoding (np.ndarray): Known face encoding to compare against
            face_encoding_to_check (np.ndarray): Face encoding to check
            tolerance (float, optional): Maximum distance threshold. Default: 0.6
        """
        return face_recognition.compare_faces(
            [known_encoding], face_encoding_to_check, tolerance)[0]
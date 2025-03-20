import dlib
import cv2
import numpy as np
from typing import Optional, List, Tuple

from src.interfaces.face_recognizer import FaceRecognizer


class DlibCnnRecognizer(FaceRecognizer):
    """
    Face recognizer implementation using dlib's CNN face detector and ResNet recognition model.
    This provides higher accuracy than HOG-based detection at the cost of more processing time.
    """

    def __init__(self, predictor_path: str, recognition_model_path: str, detector_path: str):
        # CNN face detector - more accurate than HOG but slower
        self.cnn_face_detector = dlib.cnn_face_detection_model_v1(detector_path)
        # Facial Landmarks predictor
        self.shape_predictor = dlib.shape_predictor(predictor_path)
        # Face recognition model
        self.face_encoder = dlib.face_recognition_model_v1(recognition_model_path)
        # Stricter default tolerance to reduce false positives
        self.default_tolerance = 0.49

    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        """
        Extracts face encoding from an image using CNN detection.
        Returns None if no face is detected.
        """
        if isinstance(image, str):
            image = cv2.imread(image)

        if image is None:
            return None

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Use CNN detector for more precision
        faces = self.cnn_face_detector(rgb_image, 1)

        if not faces:
            return None

        # Select the largest face (generally the closest one)
        if len(faces) > 1:
            largest_face = max(faces, key=lambda rect: rect.rect.width() * rect.rect.height())
            dlib_rect = largest_face.rect
        else:
            dlib_rect = faces[0].rect

        # Get facial landmarks
        shape = self.shape_predictor(rgb_image, dlib_rect)

        # Compute face encoding
        face_descriptor = self.face_encoder.compute_face_descriptor(rgb_image, shape)

        return np.array(face_descriptor)

    def detect_faces(self, image) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in an image using CNN detection.
        Returns a list of face locations.
        """
        if isinstance(image, str):
            image = cv2.imread(image)

        if image is None:
            return []

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Use CNN detector
        faces = self.cnn_face_detector(rgb_image, 1)

        return [(face.rect.top(), face.rect.right(),
                 face.rect.bottom(), face.rect.left())
                for face in faces]

    def compare_faces(self, known_encoding: np.ndarray,
                      face_encoding_to_check: np.ndarray,
                      tolerance: float = None) -> bool:
        """
        Compares two face encodings using Euclidean distance.
        Returns True if the distance is below the tolerance threshold.
        """
        if tolerance is None:
            tolerance = self.default_tolerance

        if isinstance(known_encoding, list):
            known_encoding = np.array(known_encoding)

        # Calculate Euclidean distance
        distance = np.linalg.norm(known_encoding - face_encoding_to_check)

        # Return comparison result with specified tolerance
        return distance <= tolerance
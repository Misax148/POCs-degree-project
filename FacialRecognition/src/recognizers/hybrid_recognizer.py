import dlib
import cv2
import numpy as np
from typing import Optional, List, Tuple

from src.interfaces.face_recognizer import FaceRecognizer


class HybridRecognizer(FaceRecognizer):
    """
    Hybrid face recognizer that uses:
    - HOG for fast face detection
    - ResNet for accurate feature extraction

    This provides a good balance between speed and accuracy.
    """

    def __init__(self, predictor_path: str, recognition_model_path: str):
        # HOG face detector (fast)
        self.face_detector = dlib.get_frontal_face_detector()

        # Facial landmarks predictor
        self.shape_predictor = dlib.shape_predictor(predictor_path)

        # ResNet model for face recognition (accurate)
        self.face_encoder = dlib.face_recognition_model_v1(recognition_model_path)

        # Stricter default tolerance to reduce false positives
        self.default_tolerance = 0.49

    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        """
        Extracts face encoding from an image using HOG detection and ResNet encoding.
        Returns None if no face is detected.
        """
        if isinstance(image, str):
            image = cv2.imread(image)

        if image is None:
            return None

        # Resize image to increase speed if too large
        h, w = image.shape[:2]
        if max(h, w) > 640:
            scale = 640 / max(h, w)
            image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Use HOG detector for faster detection
        faces = self.face_detector(rgb_image, 1)  # The second parameter can increase detection accuracy

        if not faces:
            return None

        # Select the largest face (generally the closest one)
        if len(faces) > 1:
            largest_face = max(faces, key=lambda rect: rect.width() * rect.height())
        else:
            largest_face = faces[0]

        # Get facial landmarks
        shape = self.shape_predictor(rgb_image, largest_face)

        # Compute face encoding with ResNet model
        face_descriptor = self.face_encoder.compute_face_descriptor(rgb_image, shape)

        return np.array(face_descriptor)

    def detect_faces(self, image) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in an image using HOG detection (fast).
        Returns a list of face locations.
        """
        if isinstance(image, str):
            image = cv2.imread(image)

        if image is None:
            return []

        # Resize image for faster processing if needed
        h, w = image.shape[:2]
        if max(h, w) > 640:
            scale = 640 / max(h, w)
            image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Use HOG detector with upsampling to improve detection
        faces = self.face_detector(rgb_image, 1)

        return [(face.top(), face.right(), face.bottom(), face.left())
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
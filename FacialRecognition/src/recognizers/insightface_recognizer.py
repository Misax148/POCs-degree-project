import numpy as np
import cv2
from typing import Optional, List, Tuple

from src.interfaces.face_recognizer import FaceRecognizer


class InsightFaceRecognizer(FaceRecognizer):
    """
    Face recognizer implementation using IF.
    IF provides state-of-the-art face recognition models with better accuracy
    across different ethnicities and skin tones.
    """

    def __init__(self, model_folder=None):
        """
        Initialize IF recognition model.

        Args:
            model_folder: Optional path to model folder. If None, uses default path.
        """
        try:
            # Import InsightFace here to avoid dependency issues if not installed
            import insightface
            from insightface.app import FaceAnalysis

            # Set up the face analysis app with detection and recognition
            self.app = FaceAnalysis(name="buffalo_l", root=model_folder)
            self.app.prepare(ctx_id=0, det_size=(640, 640))

            # Default tolerance threshold for face comparison
            self.default_tolerance = 0.49

            self.is_initialized = True
            print("------- IF started -------")

        except ImportError:
            self.is_initialized = False
        except Exception as e:
            print(f"ERROR initializing InsightFace: {e}")
            self.is_initialized = False

    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        """
        Extract facial features from an image using IF.
        Returns None if no face is detected.
        """
        if not self.is_initialized:
            print("IF is not initialized properly")
            return None

        # Load image if path is provided
        if isinstance(image, str):
            image = cv2.imread(image)

        if image is None:
            return None

        # Convert to RGB (InsightFace expects RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces with embeddings
        faces = self.app.get(rgb_image)

        if len(faces) == 0:
            return None

        # Get the largest face if multiple faces are detected
        if len(faces) > 1:
            # Sort by face area (bbox size)
            faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)

        # Get embedding from the first/largest face
        face_encoding = faces[0].embedding

        return face_encoding

    def detect_faces(self, image) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image using InsightFace.
        Returns a list of face locations as (top, right, bottom, left).
        """
        if not self.is_initialized:
            print("IF not initialized properly")
            return []

        if isinstance(image, str):
            image = cv2.imread(image)

        if image is None:
            return []

        # Convert to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces
        faces = self.app.get(rgb_image)

        # Convert to the format expected by our interface (top, right, bottom, left)
        face_locations = []
        for face in faces:
            bbox = face.bbox.astype(int)
            # IF returns bbox as (x1, y1, x2, y2)
            # Convert to (top, right, bottom, left)
            left, top, right, bottom = bbox
            face_locations.append((top, right, bottom, left))

        return face_locations

    def compare_faces(self, known_encoding: np.ndarray,
                      face_encoding_to_check: np.ndarray,
                      tolerance: float = None) -> bool:
        """
        Compare two face encodings using cosine similarity.
        Returns True if the similarity is above the threshold.
        """
        if not self.is_initialized:
            print("IF not initialized properly")
            return False

        if tolerance is None:
            tolerance = self.default_tolerance

        if isinstance(known_encoding, list):
            known_encoding = np.array(known_encoding)

        # Normalize vectors to unit length for cosine similarity
        known_encoding = known_encoding / np.linalg.norm(known_encoding)
        face_encoding_to_check = face_encoding_to_check / np.linalg.norm(face_encoding_to_check)

        # Calculate cosine similarity (dot product of normalized vectors)
        similarity = np.dot(known_encoding, face_encoding_to_check)

        # InsightFace uses similarity rather than distance (higher is better)
        return similarity >= (1.0 - tolerance)
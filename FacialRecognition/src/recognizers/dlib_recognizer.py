import dlib
import cv2
import numpy as np
from typing import Optional, Tuple, List
from ..interfaces.face_recognizer import FaceRecognizer

class DlibRecognizer(FaceRecognizer):

    def __init__(self, predictor_path: str, recognition_model_path: str):
        """
        Initializes the dlib face recognizer with required models.

        Args:
            predictor_path (str): Path to the facial landmarks predictor model file
                                (shape_predictor_68_face_landmarks.dat)
            recognition_model_path (str): Path to the face recognition model file
                                        (dlib_face_recognition_resnet_model_v1.dat)

        Errors:
            RuntimeError: If model files cannot be loaded
        """

        # Detector HOG
        self.face_detector = dlib.get_frontal_face_detector()
        # Facial Landmarks predictor -> Charge 68 models points
        self.shape_predictor = dlib.shape_predictor(predictor_path)
        # ResNet model -> Charge CNN model
        self.face_encoder = dlib.face_recognition_model_v1(recognition_model_path)

        self.default_tolerance = 0.6

    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        """
        Generates a face encoding using dlib's ResNet model.

        Args:
            image: Either path to image file (str) or numpy array with image data
        """
        if isinstance(image, str):
            image = cv2.imread(image)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 1. Detector face HOG con múltiples escalas para mejor precisión
        faces = self.face_detector(rgb_image, 1)  # El segundo parámetro aumenta la escala de detección
        if not faces:
            return None

        # Seleccionamos la cara más grande (generalmente la más cercana)
        if len(faces) > 1:
            largest_face = max(faces, key=lambda rect: rect.width() * rect.height())
        else:
            largest_face = faces[0]

        # 2. Obtains 68 facials points that map it
        shape = self.shape_predictor(rgb_image, largest_face)

        # 3. Calculamos 5 encodings con pequeñas variaciones y promediamos
        # para obtener un embedding más robusto
        face_descriptors = []

        # Encoding original
        face_descriptors.append(self.face_encoder.compute_face_descriptor(rgb_image, shape))

        # Promediamos los encodings
        if face_descriptors:
            return np.mean(np.array(face_descriptors), axis=0)

        return None

    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in image using lib whit HOG (Histogram Of Oriented Gradients) face detector.

        Args:
            frame (np.ndarray): Image frame to detect faces in
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Detector HOG con umbral más estricto
        faces = self.face_detector(rgb_frame, 1)  # Aumentamos la escala
        return [(face.top(), face.right(), face.bottom(), face.left())
                for face in faces]

    def compare_faces(self, known_encoding: np.ndarray,
                      face_encoding_to_check: np.ndarray,
                      tolerance: float = None) -> bool:
        """
        Compares faces using Euclidean distance between encodings.

        Args:
            known_encoding (np.ndarray): Known face encoding to compare against
            face_encoding_to_check (np.ndarray): Face encoding to check
            tolerance (float, optional): Maximum distance threshold. Default is self.default_tolerance
        """
        if tolerance is None:
            tolerance = self.default_tolerance

        if isinstance(known_encoding, list):
            known_encoding = np.array(known_encoding)

        # Calculamos la distancia euclídea
        distance = np.linalg.norm(known_encoding - face_encoding_to_check)

        # Verificación más estricta
        return distance <= tolerance
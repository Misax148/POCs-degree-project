from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Tuple, List


# Interface
class FaceRecognizer(ABC):
    """
    Abstract interface for facial recognition implementations.
    This interface defines the core methods needed for facial recognition operations.
    """

    @abstractmethod
    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        """
        This will generate a facial encoding from an image.

        Args:
            image: Can be either a path to an image file (str) or a numpy array
                  containing the image data (np.ndarray)

        Returns:
            Optional[np.ndarray]: A 128-dimensional face encoding array if a face is found,
                                None if no face is detected
        """
        pass

    @abstractmethod
    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        """
        Detects all faces in a given frame/image.

        Args:
            frame (np.ndarray): Image frame in which to detect faces

        Returns:
            List[Tuple[int, int, int, int]]: List of face locations, each as a tuple of
                                            (top, right, bottom, left) coordinates
        """
        pass

    @abstractmethod
    def compare_faces(self, known_encoding: np.ndarray,
                      face_encoding_to_check: np.ndarray,
                      tolerance: float = 0.6) -> bool:
        """
        Compares two face encodings to determine if they are of the same person.

        Args:
            known_encoding (np.ndarray): The known face encoding to compare against
            face_encoding_to_check (np.ndarray): The face encoding to check
            tolerance (float, optional): How much distance between faces to consider it a match.
                                      Lower is stricter. Default: 0.6

        Returns:
            bool: True if the faces match within the tolerance, False otherwise
        """
        pass

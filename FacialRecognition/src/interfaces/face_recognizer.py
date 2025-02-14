from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Tuple, List

# Interface
class FaceRecognizer(ABC):

    @abstractmethod
    def get_face_encoding(self, image) -> Optional[np.ndarray]:
        pass

    @abstractmethod
    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        pass

    @abstractmethod
    def compare_faces(self, known_encoding: np.ndarray,
                      face_encoding_to_check: np.ndarray,
                      tolerance: float = 0.6) -> bool:
        pass

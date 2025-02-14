import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Tuple, Optional
import os


class ImageUtils:
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        if not os.path.exists(image_path):
            return None

        try:
            return cv2.imread(image_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    @staticmethod
    def resize_image(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        return cv2.resize(image, size)

    @staticmethod
    def convert_cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv2_image)

    @staticmethod
    def convert_pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    @staticmethod
    def create_photo_image(image: np.ndarray, size: Optional[Tuple[int, int]] = None) -> ImageTk.PhotoImage:
        if size:
            image = ImageUtils.resize_image(image, size)

        pil_image = ImageUtils.convert_cv2_to_pil(image)
        return ImageTk.PhotoImage(pil_image)

    @staticmethod
    def save_image(image: np.ndarray, path: str) -> bool:
        try:
            return cv2.imwrite(path, image)
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    @staticmethod
    def validate_image(file_path: str) -> bool:
        try:
            Image.open(file_path).verify()
            return True
        except Exception:
            return False
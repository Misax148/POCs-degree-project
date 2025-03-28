import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Tuple, Optional
import os


class ImageUtils:

    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """
        Loads an image from a file path using OpenCV.

        Args:
            image_path (str): Path to the image file to load

        Returns:
            Optional[np.ndarray]: Loaded image as a numpy array in BGR format,
                                or None if loading fails
        """
        if not os.path.exists(image_path):
            return None

        try:
            return cv2.imread(image_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    @staticmethod
    def resize_image(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """
        Resizes an image to the specified dimensions.

        Args:
            image (np.ndarray): Input image as numpy array
            size (Tuple[int, int]): Target size as (width, height)
        """
        return cv2.resize(image, size)

    @staticmethod
    def convert_cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
        """
        Converts an OpenCV image (BGR) to PIL Image format (RGB).

        Args:
            cv2_image (np.ndarray): OpenCV image in BGR format
        """
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv2_image)

    @staticmethod
    def enhance_image_for_recognition(image: np.ndarray) -> np.ndarray:
        """
        Enhances an image for better face recognition.
        Applies histogram equalization to improve contrast.
        """
        if image is None:
            return None

        # Convert to grayscale if it's a color image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply histogram equalization
        equalized = cv2.equalizeHist(gray)

        # Convert back to color if the original was color
        if len(image.shape) == 3:
            result = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
            return result

        return equalized
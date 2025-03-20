from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import os
import tempfile
import shutil

from src.interfaces.face_recognizer import FaceRecognizer
from src.utils.db_manager import DBManager


class InsightFaceAPI:
    """
    API class for facial recognition using InsightFace.
    Provides endpoints for user registration and verification.
    """

    def __init__(self, app: FastAPI, recognizer: FaceRecognizer, db_manager: DBManager):
        """
        Initialize the API with FastAPI app and required components.

        Args:
            app: FastAPI application instance
            recognizer: Face recognizer implementation
            db_manager: Database manager for user data
        """
        self.app = app
        self.recognizer = recognizer
        self.db_manager = db_manager
        self._setup_routes()
        self._setup_cors()

    def _setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # All origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Set up API endpoints."""

        @self.app.post("/api/register")
        async def register_user(username: str = Form(...), image: UploadFile = File(...)):
            """
            Register a new user with facial data.

            Args:
                username: User identifier
                image: User face image
            """
            # Validate input
            self._validate_username(username)

            # Process uploaded image
            temp_file = None
            try:
                temp_file = await self._process_uploaded_image(image)
                face_encoding = self._extract_facial_features(temp_file)

                # Check if face already exists
                self._check_face_exists(face_encoding)

                # Register user in database
                self._save_user(username, face_encoding, temp_file)

                return self._create_successful_registration_response(username, face_encoding)
            finally:
                # Clean up temporary file
                self._cleanup_temp_file(temp_file)

        @self.app.post("/api/verify")
        async def verify_user(image: UploadFile = File(...)):
            """
            Verify a user using facial recognition.

            Args:
                image: User face image to verify
            """
            # Process uploaded image
            temp_file = None
            try:
                temp_file = await self._process_uploaded_image(image)
                face_encoding = self._extract_facial_features(temp_file)

                # Find matches in database
                best_match, lowest_distance = self._find_best_match(face_encoding)

                # Generate response based on result
                return self._create_verification_response(best_match, lowest_distance)
            finally:
                # Clean up temporary file
                self._cleanup_temp_file(temp_file)

        @self.app.get("/api/users")
        async def get_users():
            return self._get_user_list()

    def _validate_username(self, username):
        if not username or not username.strip():
            raise HTTPException(status_code=400, detail="Nombre de usuario requerido")

        # Check if user already exists
        if self.db_manager.user_exists(username):
            raise HTTPException(status_code=409, detail="El usuario ya existe")

    async def _process_uploaded_image(self, image):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
            temp_file = temp.name
            shutil.copyfileobj(image.file, temp)
            return temp_file

    def _extract_facial_features(self, image_path):
        face_encoding = self.recognizer.get_face_encoding(image_path)

        if face_encoding is None:
            raise HTTPException(status_code=400, detail="No se detecto ningun rostro en la imagen")

        return face_encoding

    def _check_face_exists(self, face_encoding):
        for existing_username, user_data in self.db_manager.get_all_users().items():
            stored_encoding = user_data["face_encoding"]
            if isinstance(stored_encoding, list):
                stored_encoding = np.array(stored_encoding)

            # Calculate cosine similarity
            distance = self._calculate_cosine_distance(stored_encoding, face_encoding)

            # If distance is less than threshold, face already exists
            if distance <= self.recognizer.default_tolerance:
                raise HTTPException(
                    status_code=409,
                    detail=f"Este rostro ya esta registrado con el nombre de usuario '{existing_username}'"
                )

    def _calculate_cosine_distance(self, encoding1, encoding2):
        # Normalize vectors for cosine similarity
        encoding1_norm = encoding1 / np.linalg.norm(encoding1)
        encoding2_norm = encoding2 / np.linalg.norm(encoding2)

        # Calculate cosine similarity
        similarity = np.dot(encoding1_norm, encoding2_norm)
        distance = 1.0 - similarity  # Convert similarity to distance
        return distance

    def _save_user(self, username, face_encoding, image_path):
        success = self.db_manager.save_user(username, face_encoding, image_path)

        if not success:
            raise HTTPException(status_code=500, detail="Error al guardar el usuario en la base de datos")

    def _create_successful_registration_response(self, username, face_encoding):
        return JSONResponse(
            status_code=201,
            content={
                "message": "Usuario registrado correctamente",
                "username": username,
                "dimensions": len(face_encoding)
            }
        )

    def _find_best_match(self, face_encoding):
        best_match = None
        lowest_distance = float('inf')

        # Check all users
        for username, user_data in self.db_manager.get_all_users().items():
            stored_encoding = user_data["face_encoding"]
            if isinstance(stored_encoding, list):
                stored_encoding = np.array(stored_encoding)

            # Calculate cosine distance
            distance = self._calculate_cosine_distance(stored_encoding, face_encoding)

            # Update best match
            if distance < lowest_distance:
                lowest_distance = distance
                best_match = username

        return best_match, lowest_distance

    def _create_verification_response(self, best_match, match_distance):
        tolerance = self.recognizer.default_tolerance

        if best_match and match_distance <= tolerance:
            # Get user data for response
            user_data = self.db_manager.get_user(best_match)

            # Get image path and convert to URL
            full_image_path = user_data.get("image_path", "")
            image_name = os.path.basename(full_image_path) if full_image_path else ""
            image_url = f"/api/image/{image_name}" if image_name else ""

            # Calculate confidence level (0-100%)
            confidence = max(0, min(100, (1 - match_distance / tolerance) * 100))

            # Determine security level
            if confidence > 95:
                security_level = "ALTO"
            elif confidence > 85:
                security_level = "MEDIO"
            else:
                security_level = "BAJO"

            return JSONResponse(
                content={
                    "found": True,
                    "username": best_match,
                    "distance": float(match_distance),
                    "tolerance": float(tolerance),
                    "confidence": float(confidence),
                    "security_level": security_level,
                    "image_path": image_url
                }
            )
        else:
            # No match found or confidence too low
            message = "No se encontro coincidencia."
            if best_match:
                message = f"La mas cercana fue '{best_match}' con distancia {float(match_distance):.4f} (umbral: {float(tolerance)})"

            return JSONResponse(
                content={
                    "found": False,
                    "message": message
                }
            )

    def _get_user_list(self):
        users = self.db_manager.get_all_users()
        return JSONResponse(
            content={
                "users": [
                    {
                        "username": username,
                        "created_at": user_data.get("created_at", ""),
                        "image_path": f"/api/image/{os.path.basename(user_data.get('image_path', ''))}"
                    }
                    for username, user_data in users.items()
                ]
            }
        )

    def _cleanup_temp_file(self, temp_file):
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)
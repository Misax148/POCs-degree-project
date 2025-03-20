import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AuthPage.css";
import useFaceApi from "../hooks/useFaceApi";
import WebcamCapture from "../components/camera/WebcamCapture";
import AuthToggle from "../components/ui/AuthToggle";
import LoadingButton from "../components/ui/LoadingButton";
import authService from "../services/authService";

/**
 * Main page where facial detection starts
 */
const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const navigate = useNavigate();
  const { isModelLoaded } = useFaceApi();

  if (!isModelLoaded) {
    return <div className="loading">Loading face detection models...</div>;
  }

  const handleToggleMode = (loginMode) => {
    setIsLogin(loginMode);
    resetForm();
  };

  const handleStartCamera = () => {
    setIsCameraOn(true);
    setCapturedImage(null);
  };

  const handleStopCamera = () => {
    setIsCameraOn(false);
    setCapturedImage(null);
  };

  const handleCapture = (imageSrc) => {
    setCapturedImage(imageSrc);
    setIsCameraOn(false);
  };

  const resetForm = () => {
    setCapturedImage(null);
    setError(null);
    setIsCameraOn(false);
    if (!isLogin) {
      setUsername("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!capturedImage) {
      setError({ message: "Please capture an image first", type: "error" });
      return;
    }

    if (!isLogin && !username.trim()) {
      setError({ message: "Please enter a username", type: "error" });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      if (isLogin) {
        const response = await authService.verify(capturedImage);

        if (response.found) {
          navigate("/welcome", {
            state: {
              username: response.username,
              userImage: response.image_path,
              distance: response.distance,
              tolerance: response.tolerance,
              confidence: response.confidence
            },
          });
        } else {
          setError({
            message: response.message || "User not found",
            type: "error",
          });
        }
      } else {
        await authService.register(username, capturedImage);
        setError({
          message: "Registration successful! You can now login.",
          type: "success",
        });
        setIsLogin(true);
      }
    } catch (err) {
      console.error("Error in authentication:", err);
      setError({ message: err.message || "An error occurred", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="auth-container">
        <h1>{isLogin ? "Facial Login" : "Facial Registration"}</h1>

        <AuthToggle isLogin={isLogin} onToggle={handleToggleMode} />

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label>Username:</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
          )}

          <div className="camera-controls">
            {!isCameraOn && !capturedImage ? (
              <button
                type="button"
                onClick={handleStartCamera}
                className="camera-btn"
              >
                Turn On Camera
              </button>
            ) : (
              !capturedImage && (
                <button
                  type="button"
                  onClick={handleStopCamera}
                  className="camera-btn stop"
                >
                  Turn Off Camera
                </button>
              )
            )}
          </div>

          <WebcamCapture isActive={isCameraOn} onCapture={handleCapture} />

          {capturedImage && (
            <div className="preview-container">
              <h3>Preview</h3>
              <img
                src={capturedImage}
                alt="Captured"
                className="preview-image"
              />
              <button
                type="button"
                className="recapture-btn"
                onClick={handleStartCamera}
              >
                Retake Photo
              </button>
            </div>
          )}

          {error &&
            (typeof error === "object" ? (
              <div className={`message ${error.type}`}>{error.message}</div>
            ) : (
              <div className="message error">{error}</div>
            ))}

          <LoadingButton
            type="submit"
            className="submit-btn"
            isLoading={isLoading}
            disabled={isLoading || !capturedImage}
            loadingText="Processing..."
          >
            {isLogin ? "Login" : "Sign Up"}
          </LoadingButton>
        </form>
      </div>
    </div>
  );
};

export default AuthPage;

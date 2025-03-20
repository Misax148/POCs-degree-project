import React, { useRef, useEffect } from "react";
import Webcam from "react-webcam";
import FaceIndicators from "./FaceIndicators";
import useFaceDetection from "../../hooks/useFaceDetection";
import { adjustImageBrightness } from "../../utils/faceUtils";

/**
 * Captura webcam with facial detection
 */
const WebcamCapture = ({ onCapture, isActive }) => {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);

  const { faceStatus, startDetection, stopDetection, isReady } =
    useFaceDetection(webcamRef, canvasRef, isActive);

  // Init detection before 1000ms to stabilicier camera
  useEffect(() => {
    let timeoutId;

    if (isActive) {
      timeoutId = setTimeout(() => {
        startDetection();
      }, 1000);
    }

    return () => {
      clearTimeout(timeoutId);
      stopDetection();
    };
  }, [isActive, startDetection, stopDetection]);

  // Take photo
  const handleCapture = async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();

      try {
        // Improve image captured
        const processedImage = await adjustImageBrightness(imageSrc);
        onCapture(processedImage);
      } catch (error) {
        console.error("Error processing image:", error);
        onCapture(imageSrc);
      }
    }
  };

  // If camaera is not active, don't show nothing
  if (!isActive) return null;

  return (
    <div className="webcam-container">
      <Webcam
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={640}
        height={480}
        videoConstraints={{
          width: 640,
          height: 480,
          facingMode: "user",
        }}
      />
      <canvas
        ref={canvasRef}
        className="face-canvas"
        width={640}
        height={480}
      />

      <FaceIndicators faceStatus={faceStatus} />

      <button
        type="button"
        onClick={handleCapture}
        className={`capture-btn ${isReady ? "ready" : ""}`}
        disabled={!isReady}
      >
        {isReady ? "Capture Photo" : "Position Face Correctly"}
      </button>
    </div>
  );
};

export default WebcamCapture;

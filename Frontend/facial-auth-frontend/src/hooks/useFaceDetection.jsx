import { useState, useEffect, useRef } from "react";
import * as faceapi from "face-api.js";

/**
 * Hook to handle facial detection and status
 */
export const useFaceDetection = (webcamRef, canvasRef, isActive) => {
  const [faceStatus, setFaceStatus] = useState({
    detected: false,
    centered: false,
    aligned: false,
  });
  const detectIntervalRef = useRef(null);

  useEffect(() => {
    return () => stopDetection();
  }, []);

  // Init or stop when detection change to isActive
  useEffect(() => {
    if (isActive) {
      startDetection();
    } else {
      stopDetection();
      setFaceStatus({ detected: false, centered: false, aligned: false });
    }
  }, [isActive]);

  // Start face detection
  const startDetection = () => {
    if (detectIntervalRef.current) return;

    detectIntervalRef.current = setInterval(async () => {
      if (webcamRef.current && webcamRef.current.video?.readyState === 4) {
        const video = webcamRef.current.video;
        const canvas = canvasRef.current;

        if (!canvas) return;

        const displaySize = { width: video.width, height: video.height };

        const detections = await faceapi
          .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
          .withFaceLandmarks();

        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (detections && detections.length === 1) {
          const detection = detections[0];
          const resizedDetection = faceapi.resizeResults(
            detection,
            displaySize
          );

          const isCentered = checkFaceCentered(resizedDetection, displaySize);
          const isAligned = checkFaceAlignment(resizedDetection.landmarks);

          const newStatus = {
            detected: true,
            centered: isCentered,
            aligned: isAligned,
          };

          setFaceStatus(newStatus);
          drawDetectionWithStatus(canvas, resizedDetection, {
            isCentered,
            isAligned,
          });
        } else {
          setFaceStatus({ detected: false, centered: false, aligned: false });
        }
      }
    }, 100);
  };

  const stopDetection = () => {
    if (detectIntervalRef.current) {
      clearInterval(detectIntervalRef.current);
      detectIntervalRef.current = null;
    }
  };

  return {
    faceStatus,
    startDetection,
    stopDetection,
    isReady: faceStatus.detected && faceStatus.centered && faceStatus.aligned,
  };
};

// Aux function for check if face is centered
const checkFaceCentered = (detection, displaySize) => {
  const faceBox = detection.detection.box;
  const centerX = faceBox.x + faceBox.width / 2;
  const centerY = faceBox.y + faceBox.height / 2;

  const isXCentered =
    Math.abs(centerX - displaySize.width / 2) < displaySize.width * 0.2;
  const isYCentered =
    Math.abs(centerY - displaySize.height / 2) < displaySize.height * 0.2;

  return isXCentered && isYCentered;
};

// Aux function for check if face is Align
const checkFaceAlignment = (landmarks) => {
  const leftEye = landmarks.getLeftEye();
  const rightEye = landmarks.getRightEye();

  const leftEyeCenter = leftEye.reduce(
    (acc, point) => ({ x: acc.x + point.x, y: acc.y + point.y }),
    { x: 0, y: 0 }
  );
  const rightEyeCenter = rightEye.reduce(
    (acc, point) => ({ x: acc.x + point.x, y: acc.y + point.y }),
    { x: 0, y: 0 }
  );

  leftEyeCenter.x /= leftEye.length;
  leftEyeCenter.y /= leftEye.length;
  rightEyeCenter.x /= rightEye.length;
  rightEyeCenter.y /= rightEye.length;

  const eyeAngle = Math.abs(
    Math.atan2(
      rightEyeCenter.y - leftEyeCenter.y,
      rightEyeCenter.x - leftEyeCenter.x
    ) *
      (180 / Math.PI)
  );

  return eyeAngle < 10;
};

// If face is well posisioned, this will show status 
const drawDetectionWithStatus = (canvas, detection, status) => {
  const ctx = canvas.getContext("2d");
  const box = detection.detection.box;

  ctx.strokeStyle =
    status.isCentered && status.isAligned ? "#00ff00" : "#ff0000";
  ctx.lineWidth = 2;
  ctx.strokeRect(box.x, box.y, box.width, box.height);

  ctx.font = "16px Arial";
  ctx.fillStyle = "#fff";

  let text =
    status.isCentered && status.isAligned
      ? "Face Well Positioned"
      : "Adjust Face Position";

  const textWidth = ctx.measureText(text).width;

  ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
  ctx.fillRect(box.x, box.y - 25, textWidth + 10, 20);

  ctx.fillStyle = "#fff";
  ctx.fillText(text, box.x + 5, box.y - 10);
};

export default useFaceDetection;

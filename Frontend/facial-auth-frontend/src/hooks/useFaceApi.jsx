import { useState, useEffect } from "react";
import * as faceapi from "face-api.js";

/**
 * Hook to charge face-api.js models
 */
export const useFaceApi = () => {
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const loadModels = async () => {
      try {
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri("/models"),
          faceapi.nets.faceLandmark68Net.loadFromUri("/models"),
          faceapi.nets.faceExpressionNet.loadFromUri("/models"),
        ]);

        if (isMounted) {
          setIsModelLoaded(true);
        }
      } catch (err) {
        console.error("Error loading face-api models:", err);
        if (isMounted) {
          setError(err);
        }
      }
    };

    loadModels();

    return () => {
      isMounted = false;
    };
  }, []);

  return { isModelLoaded, error };
};

export default useFaceApi;

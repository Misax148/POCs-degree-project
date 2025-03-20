import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./WelcomePage.css";

const WelcomePage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const { username, userImage, distance, tolerance, confidence } = location.state || {};

  const calculateSimilarity = () => {
    if (distance === undefined || tolerance === undefined) {
      return confidence || "N/A"; 
    }
    
    const similarity = Math.max(0, Math.min(100, ((1 - distance / tolerance) * 100)));
    return similarity.toFixed(2);
  };

  useEffect(() => {
    if (!username) {
      navigate("/");
    }
  }, [username, navigate]);

  if (!username) {
    return null;
  }

  return (
    <div className="welcome-container">
      <div className="welcome-card">
        <h1>Welcome, {username}!</h1>

        {userImage && (
          <div className="profile-container">
            <img
              src={`http://localhost:8000${userImage}`}
              alt="Profile"
              className="profile-image"
              onError={(e) => {
                console.error("Error loading image:", userImage);
                e.target.src = "/placeholder-profile.png";
                e.target.className = "profile-image error";
              }}
            />
          </div>
        )}

        <div className="verification-details">
          <p className="success-message">Authentication successful!</p>
        </div>

        <button onClick={() => navigate("/")} className="back-btn">
          Back to Home
        </button>
      </div>
    </div>
  );
};

export default WelcomePage;
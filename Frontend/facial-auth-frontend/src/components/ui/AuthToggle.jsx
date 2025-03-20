import React from "react";

/**
 * Altern between auth modes like login or signup
 */
const AuthToggle = ({ isLogin, onToggle }) => {
  return (
    <div className="toggle-buttons">
      <button
        onClick={() => onToggle(true)}
        className={isLogin ? "active" : "inactive"}
      >
        Login
      </button>
      <button
        onClick={() => onToggle(false)}
        className={!isLogin ? "active" : "inactive"}
      >
        Sign Up
      </button>
    </div>
  );
};

export default AuthToggle;

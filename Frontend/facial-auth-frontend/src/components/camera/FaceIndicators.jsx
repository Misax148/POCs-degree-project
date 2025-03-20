import React from 'react';

/**
 * Showing status of facial detection
 */
const FaceIndicators = ({ faceStatus }) => {
  const { detected, centered, aligned } = faceStatus;
  
  return (
    <div className="status-indicators">
      <div className={`indicator ${detected ? 'good' : 'bad'}`}>
        Face Detected
      </div>
      <div className={`indicator ${centered ? 'good' : 'bad'}`}>
        Face Centered
      </div>
      <div className={`indicator ${aligned ? 'good' : 'bad'}`}>
        Face Aligned
      </div>
    </div>
  );
};

export default FaceIndicators;
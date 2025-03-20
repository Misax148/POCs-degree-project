import React from "react";

/**
 * Status charge button
 */
const LoadingButton = ({
  isLoading,
  disabled,
  className = "",
  loadingText = "Processing...",
  children,
  ...rest
}) => {
  const buttonClass = [className, isLoading ? "loading" : ""]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={buttonClass} disabled={disabled || isLoading} {...rest}>
      {isLoading ? loadingText : children}
    </button>
  );
};

export default LoadingButton;

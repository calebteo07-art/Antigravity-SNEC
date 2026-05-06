import React from "react";

interface EyeQLogoProps {
  size?: number;
  className?: string;
  variant?: "light" | "dark";
}

export function EyeQLogo({ size = 48, className = "", variant = "light" }: EyeQLogoProps) {
  const irisColor = variant === "light" ? "#14B8A6" : "#14B8A6";
  const pupilColor = variant === "light" ? "#0D1B2A" : "#0D1B2A";
  const outlineColor = variant === "light" ? "#FFFFFF" : "#0D1B2A";

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer eye shape */}
      <ellipse cx="24" cy="24" rx="22" ry="14" fill={outlineColor} opacity="0.1" />
      <path
        d="M2 24 C8 10, 40 10, 46 24 C40 38, 8 38, 2 24Z"
        fill={variant === "light" ? "#0D1B2A" : "#FFFFFF"}
        opacity="0.08"
      />
      {/* Eye outline */}
      <path
        d="M2 24 C8 10, 40 10, 46 24 C40 38, 8 38, 2 24Z"
        stroke={variant === "light" ? "#FFFFFF" : "#0D1B2A"}
        strokeWidth="1.5"
        fill="none"
        opacity="0.6"
      />
      {/* Iris */}
      <circle cx="24" cy="24" r="10" fill={irisColor} />
      {/* Iris detail */}
      <circle cx="24" cy="24" r="10" fill="none" stroke="#0D9488" strokeWidth="1" opacity="0.5" />
      {/* Pupil */}
      <circle cx="24" cy="24" r="5" fill={pupilColor} />
      {/* Highlight */}
      <circle cx="27" cy="21" r="2" fill="white" opacity="0.7" />
      {/* Small highlight */}
      <circle cx="22" cy="26" r="1" fill="white" opacity="0.4" />
    </svg>
  );
}

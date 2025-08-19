"use client";
import React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
};

const Button: React.FC<Props> = ({ children, loading, className = "", ...rest }) => (
  <button
    {...rest}
    className={`px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed ${className}`}
  >
    {loading ? "Loading..." : children}
  </button>
);

export default Button;

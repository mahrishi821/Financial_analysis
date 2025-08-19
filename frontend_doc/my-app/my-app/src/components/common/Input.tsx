"use client";
import React from "react";

type Props = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  hint?: string;
};

const Input: React.FC<Props> = ({ label, hint, className = "", ...rest }) => (
  <div>
    {label && <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>}
    <input
      {...rest}
      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    />
    {hint && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
  </div>
);

export default Input;

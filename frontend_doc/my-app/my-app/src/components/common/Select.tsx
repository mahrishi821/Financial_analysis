"use client";
import React from "react";

type Props = React.SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
};

const Select: React.FC<Props> = ({ label, className = "", children, ...rest }) => (
  <div>
    {label && <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>}
    <select
      {...rest}
      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    >
      {children}
    </select>
  </div>
);

export default Select;

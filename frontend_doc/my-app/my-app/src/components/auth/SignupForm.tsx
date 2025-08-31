"use client";
import React, { useState } from "react";
import { useSignup } from "@/hooks/useSignup";

const SignupForm = () => {
  const { signup, loading, error } = useSignup();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
    dob: "",
    phone_number: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await signup(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="text-red-500">{error}</p>}
      <input
        name="name"
        placeholder="Full Name"
        className="w-full border rounded p-2"
        value={form.name}
        onChange={handleChange}
        required
      />
      <input
        type="email"
        name="email"
        placeholder="Email"
        className="w-full border rounded p-2"
        value={form.email}
        onChange={handleChange}
        required
      />
      <input
        type="password"
        name="password"
        placeholder="Password"
        className="w-full border rounded p-2"
        value={form.password}
        onChange={handleChange}
        required
      />
      <input
        type="password"
        name="confirm_password"
        placeholder="Confirm Password"
        className="w-full border rounded p-2"
        value={form.confirm_password}
        onChange={handleChange}
        required
      />
      <input
        type="date"
        name="dob"
        className="w-full border rounded p-2"
        value={form.dob}
        onChange={handleChange}
        required
      />
      <input
        type="tel"
        name="phone_number"
        placeholder="Phone (optional)"
        className="w-full border rounded p-2"
        value={form.phone_number}
        onChange={handleChange}
      />
      <button
        type="submit"
        className="w-full bg-green-600 text-white py-2 rounded"
        disabled={loading}
      >
        {loading ? "Creating account..." : "Sign Up"}
      </button>
    </form>
  );
};

export default SignupForm;

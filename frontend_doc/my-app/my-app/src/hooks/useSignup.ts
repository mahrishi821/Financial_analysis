import { useState } from "react";
import { signupApi } from "@/service/api/auth";

export const useSignup = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const signup = async (data: {
    name: string;
    email: string;
    password: string;
    confirm_password: string;
    dob: string;
    phone_number?: string;
  }) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await signupApi(data);
      if (res.success) {
        setSuccess(res.data); // "User created successfully"
      } else {
        setError(res.message || "Signup failed");
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return { signup, loading, error, success };
};

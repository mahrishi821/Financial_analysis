import { useState } from "react";
import { useRouter } from "next/navigation";   // ✅ import router
import { loginApi } from "@/service/api/auth"; // also note: it should be services not service
import { useAuth } from "./useAuth";

export const useLogin = () => {
  const { login: setAuth } = useAuth();
  const router = useRouter();   // ✅ create router instance
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await loginApi(email, password);
      console.log("Login API Response:", res);

      if (res.success) {
        setAuth(res.data); // res.data = { access, refresh }
        router.push("/dashboard");  // ✅ now works
      } else {
        setError(res.message || "Login failed");
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return { login, loading, error };
};

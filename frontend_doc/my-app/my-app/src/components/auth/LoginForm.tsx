"use client";
import React, { useState } from "react";
import { Eye, EyeOff, Shield, Lock, User, Mail, Phone, Calendar } from "lucide-react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/context/AuthContext";
import Cookies from "js-cookie";
import { loginApi, signupApi } from "@/service/api/auth";
const API_BASE =  "http://localhost:8000/api";

const FinancialAuthForm = () => {
  const router = useRouter();
  const { login: loginCtx } = useAuthContext();

  // State management
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Auth states
  const [loginLoading, setLoginLoading] = useState(false);
  const [signupLoading, setSignupLoading] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [signupError, setSignupError] = useState("");
  const [success, setSuccess] = useState("");

  // Form data
  const [loginData, setLoginData] = useState({ email: "", password: "" });
  const [signupData, setSignupData] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
    dob: "",
    phone_number: "",
  });

  // Validation state
  const [errors, setErrors] = useState<any>({});

  // 🔹 API functions
  const login = async (email: string, password: string) => {
    setLoginLoading(true);
    setLoginError("");
    try {
      const response = await loginApi(email, password);

       const { access, refresh } = response.data;
       console.log("access token",access)
       console.log("refresh token",refresh)



      if (access && refresh) {
        // Store via context (writes localStorage + cookies and redirects)
        loginCtx({ access, refresh });
      } else if (access) {
        // If only access is provided (no refresh), set cookie locally so middleware allows dashboard
        const isProd = process.env.NODE_ENV === "production";
        Cookies.set("access_token", access, {
          secure: isProd,
          sameSite: isProd ? "strict" : "lax",
          path: "/",
        });
        localStorage.setItem("access_token", access);
        setTimeout(() => router.push("/dashboard"), 500);
      } else {
        throw new Error("Login response missing access token");
      }

      setSuccess("Login successful! Redirecting...");
    } catch (error: any) {
      setLoginError(error.message || "Invalid email or password");
    } finally {
      setLoginLoading(false);
    }
  };

  const signup = async (data: any) => {
    setSignupLoading(true);
    setSignupError("");
    try {
      await signupApi(data);
      setSuccess("Account created! Please verify your email.");
      setTimeout(() => setIsLogin(true), 2000);
    } catch (error: any) {
      setSignupError(error.message || "Signup failed");
    } finally {
      setSignupLoading(false);
    }
  };

  // Validation
  const validateForm = (data: any, isLoginForm: boolean) => {
    const newErrors: any = {};
    if (isLoginForm) {
      if (!data.email) newErrors.email = "Email is required";
      else if (!/\S+@\S+\.\S+/.test(data.email))
        newErrors.email = "Email is invalid";
      if (!data.password) newErrors.password = "Password is required";
    } else {
      if (!data.name) newErrors.name = "Full name is required";
      if (!data.email) newErrors.email = "Email is required";
      else if (!/\S+@\S+\.\S+/.test(data.email))
        newErrors.email = "Email is invalid";
      if (!data.password) newErrors.password = "Password is required";
      else if (data.password.length < 8)
        newErrors.password = "Password must be at least 8 characters";
      if (!data.confirm_password)
        newErrors.confirm_password = "Please confirm your password";
      else if (data.password !== data.confirm_password)
        newErrors.confirm_password = "Passwords do not match";
      if (!data.dob) newErrors.dob = "Date of birth is required";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handlers
  const handleLogin = async () => {
    if (validateForm(loginData, true)) {
      await login(loginData.email, loginData.password);
    }
  };

  const handleSignup = async () => {
    if (validateForm(signupData, false)) {
      await signup(signupData);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center p-4 relative">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        ></div>
      </div>

      <div className="w-full max-w-md transform transition-all duration-500 hover:scale-[1.02]">
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden relative z-10">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-center">
            <div className="flex justify-center items-center mb-4">
              <div className="bg-white/20 p-3 rounded-2xl">
                <Shield className="w-8 h-8 text-white" />
              </div>
            </div>
            <h1 className="text-2xl font-bold text-white mb-1">
              SecureFinance
            </h1>
            <p className="text-indigo-100 text-sm">
              Bank-grade security • SSL encrypted
            </p>
          </div>

          {/* Toggle */}
          <div className="p-4 pb-2">
            <div className="flex bg-gray-100 rounded-xl p-1 mb-4">
              <button
                type="button"
                onClick={() => setIsLogin(true)}
                className={`flex-1 py-2 px-4 rounded-lg text-sm font-semibold ${
                  isLogin
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setIsLogin(false)}
                className={`flex-1 py-2 px-4 rounded-lg text-sm font-semibold ${
                  !isLogin
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                }`}
              >
                Sign Up
              </button>
            </div>

            {/* Error / Success */}
            {(loginError || signupError) && (
              <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-xs">
                  {loginError || signupError}
                </p>
              </div>
            )}
            {success && (
              <div className="mb-3 p-2 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-700 text-xs">{success}</p>
              </div>
            )}

            {/* Forms */}
            {isLogin ? (
              <div className="space-y-3 animate-in slide-in-from-left duration-300">
                <InputField
                  icon={Mail}
                  type="email"
                  placeholder="Email address"
                  value={loginData.email}
                  onChange={(e) =>
                    setLoginData({ ...loginData, email: e.target.value })
                  }
                  error={errors.email}
                />
                <InputField
                  icon={Lock}
                  type="password"
                  placeholder="Password"
                  value={loginData.password}
                  onChange={(e) =>
                    setLoginData({ ...loginData, password: e.target.value })
                  }
                  error={errors.password}
                  showPasswordToggle
                  showPassword={showPassword}
                  onTogglePassword={() => setShowPassword(!showPassword)}
                />
                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center text-gray-700">
                    <input
                      type="checkbox"
                      className="mr-2 rounded text-indigo-600 focus:ring-indigo-500"
                    />
                    Remember me
                  </label>
                  <button
                    type="button"
                    className="text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Forgot password?
                  </button>
                </div>
                <button
                  type="button"
                  onClick={handleLogin}
                  disabled={loginLoading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
                >
                  {loginLoading ? "Signing in..." : "Sign In Securely"}
                </button>
              </div>
            ) : (
              <div className="space-y-3 animate-in slide-in-from-right duration-300">
                <div className="grid grid-cols-2 gap-3">
                  <InputField
                    icon={User}
                    placeholder="Full Name"
                    value={signupData.name}
                    onChange={(e) =>
                      setSignupData({ ...signupData, name: e.target.value })
                    }
                    error={errors.name}
                    compact
                  />
                  <InputField
                    icon={Mail}
                    type="email"
                    placeholder="Email"
                    value={signupData.email}
                    onChange={(e) =>
                      setSignupData({ ...signupData, email: e.target.value })
                    }
                    error={errors.email}
                    compact
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <InputField
                    icon={Lock}
                    type="password"
                    placeholder="Password"
                    value={signupData.password}
                    onChange={(e) =>
                      setSignupData({ ...signupData, password: e.target.value })
                    }
                    error={errors.password}
                    showPasswordToggle
                    showPassword={showPassword}
                    onTogglePassword={() => setShowPassword(!showPassword)}
                    compact
                  />
                  <InputField
                    icon={Lock}
                    type="password"
                    placeholder="Confirm"
                    value={signupData.confirm_password}
                    onChange={(e) =>
                      setSignupData({
                        ...signupData,
                        confirm_password: e.target.value,
                      })
                    }
                    error={errors.confirm_password}
                    showPasswordToggle
                    showPassword={showConfirmPassword}
                    onTogglePassword={() =>
                      setShowConfirmPassword(!showConfirmPassword)
                    }
                    compact
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <InputField
                    icon={Calendar}
                    type="date"
                    placeholder="DOB"
                    value={signupData.dob}
                    onChange={(e) =>
                      setSignupData({ ...signupData, dob: e.target.value })
                    }
                    error={errors.dob}
                    compact
                  />
                  <InputField
                    icon={Phone}
                    type="tel"
                    placeholder="Phone (Optional)"
                    value={signupData.phone_number}
                    onChange={(e) =>
                      setSignupData({
                        ...signupData,
                        phone_number: e.target.value,
                      })
                    }
                    compact
                  />
                </div>
                <div className="flex items-center space-x-2 text-xs text-gray-700">
                  <input
                    type="checkbox"
                    className="rounded text-indigo-600 focus:ring-indigo-500"
                    required
                  />
                  <span>
                    I agree to{" "}
                    <button
                      type="button"
                      className="text-indigo-600 hover:underline font-medium"
                    >
                      Terms
                    </button>{" "}
                    &{" "}
                    <button
                      type="button"
                      className="text-indigo-600 hover:underline font-medium"
                    >
                      Privacy
                    </button>
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleSignup}
                  disabled={signupLoading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50"
                >
                  {signupLoading ? "Creating..." : "Create Account"}
                </button>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-4 pb-4">
            <div className="pt-3 border-t border-gray-100">
              <div className="flex justify-center items-center space-x-3 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <Shield className="w-3 h-3 text-indigo-500" />
                  <span>256-bit SSL</span>
                </div>
                <div className="w-1 h-1 bg-gray-300 rounded-full"></div>
                <div className="flex items-center space-x-1">
                  <Lock className="w-3 h-3 text-purple-500" />
                  <span>Bank Security</span>
                </div>
                <div className="w-1 h-1 bg-gray-300 rounded-full"></div>
                <span>FDIC Insured</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// InputField component
const InputField = ({
  icon: Icon,
  type = "text",
  placeholder,
  value,
  onChange,
  error,
  showPasswordToggle = false,
  showPassword: currentShowPassword,
  onTogglePassword,
  compact = false,
}: {
  icon: any;
  type?: string;
  placeholder: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  showPasswordToggle?: boolean;
  showPassword?: boolean;
  onTogglePassword?: () => void;
  compact?: boolean;
}) => (
  <div className="relative">
    <Icon
      className={`absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 ${
        compact ? "w-4 h-4" : "w-5 h-5"
      }`}
    />
    <input
      type={
        showPasswordToggle
          ? currentShowPassword
            ? "text"
            : "password"
          : type
      }
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={`w-full ${
        compact ? "pl-9 pr-10 py-2 text-sm" : "pl-10 pr-12 py-3"
      } rounded-xl border-2 bg-gray-50 focus:bg-white transition-all duration-200
        ${
          error
            ? "border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-100"
            : "border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 hover:border-gray-300"
        } focus:outline-none placeholder-gray-500`}
    />
    {showPasswordToggle && (
      <button
        type="button"
        onClick={onTogglePassword}
        className={`absolute ${
          compact ? "right-2" : "right-3"
        } top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600`}
      >
        {currentShowPassword ? (
          <EyeOff className={compact ? "w-4 h-4" : "w-5 h-5"} />
        ) : (
          <Eye className={compact ? "w-4 h-4" : "w-5 h-5"} />
        )}
      </button>
    )}
    {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
  </div>
);

export default FinancialAuthForm;

"use client";
import React from "react";
import { Calendar, Mail, Phone, User, LogOut } from "lucide-react";
import { useUser } from "@/context/UserContext";
import { useAuth } from "@/hooks/useAuth";

const UserProfile: React.FC = () => {
  const user = useUser();
  const { logout } = useAuth();
  
  const handleLogout = () => {
    logout();
  };

  return (
    <div className="space-y-4 relative h-full">
      <div className="flex justify-center mb-6">
        <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center">
          {user.profilePicture ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={user.profilePicture} alt="Profile" className="w-20 h-20 rounded-full object-cover" />
          ) : (
            <User className="w-10 h-10 text-gray-400" />
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
            Full Name
          </label>
          <p className="text-gray-900 font-medium">{user.name} {user.surname}</p>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
            Date of Birth
          </label>
          <div className="flex items-center text-gray-700">
            <Calendar className="w-4 h-4 mr-2 text-gray-400" />
            {new Date(user.dateOfBirth).toLocaleDateString()}
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
            Email
          </label>
          <div className="flex items-center text-gray-700">
            <Mail className="w-4 h-4 mr-2 text-gray-400" />
            <span className="text-sm">{user.email}</span>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
            Phone
          </label>
          <div className="flex items-center text-gray-700">
            <Phone className="w-4 h-4 mr-2 text-gray-400" />
            {user.phone}
          </div>
        </div>
      </div>

      <div className="absolute bottom- -5 left-0 right-0 px-6">
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center px-4 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
        >
          <LogOut className="w-5 h-5 mr-2" />
          Logout
        </button>
      </div>
    </div>
  );
};

export default UserProfile;

"use client";
import React, { createContext, useContext, useMemo } from "react";
import type { UserProfile } from "@/types";

const defaultUser: UserProfile = {
  name: "John",
  surname: "Doe",
  dateOfBirth: "1990-05-15",
  email: "john.doe@company.com",
  phone: "+1 (555) 123-4567",
  profilePicture: ""
};

const UserContext = createContext<UserProfile>(defaultUser);

export const UserProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const value = useMemo(() => defaultUser, []);
  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export const useUser = () => useContext(UserContext);

import api from "./index";

export type UserInfo = {
  name: string;
  email: string;
};

function extractUserInfo(payload: any): UserInfo {
  // Expecting { success, message, data: { name, email } }
  try {
    const data = payload?.data ?? payload;
    const name = typeof data?.name === "string" ? data.name : "";
    const email = typeof data?.email === "string" ? data.email : "";
    return { name, email };
  } catch {
    return { name: "", email: "" };
  }
}

export const userApi = {
  getUserInfo: async (): Promise<UserInfo> => {
    const res = await api.get("/userinfo/");
    return extractUserInfo(res.data);
  },
};


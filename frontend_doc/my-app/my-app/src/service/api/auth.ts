import api from "./index";

// export const loginApi = async (email: string, password: string) => {
//   const response = await api.post("/login/", { email, password });
//   console.log(response)
//   return response.data;
// };
export const loginApi = async (email: string, password: string) => {
  const response = await api.post(
    "/login/",
    { email, password },
    { headers: { "Content-Type": "application/json" } } // force JSON
  );
  return response.data;
};


export const signupApi = async (data: {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
  dob: string;
  phone_number?: string;
}) => {
  const response = await api.post("/signup/", data);
  return response.data;
};

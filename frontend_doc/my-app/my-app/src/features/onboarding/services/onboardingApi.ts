import api from "@/service/api";

export type OnboardingPayload = {
  company_name: string;
  sector: string;
  sub_sector: string;
  country: string;
  incorporation_date: string;
  contact_person_name: string;
  contact_email: string;
  phone: string;
  frequency: string;
  status: "Active" | "Inactive" | "Offboarded";
};

export const onboardingApi = {
  createCompany: async (payload: OnboardingPayload) => {
    const res = await api.post("/companies/", payload);
    return res.data;
  },
};

import api from "@/service/api";

export type DashboardMetrics = {
  reportsGenerated: number;
  chatbotSessions: number;
  companiesOnboarded: number;
  assetAnalysisCount: number;
};

function extractWrappedNumber(payload: any, key: string): number {
  // Expect shape: { success, message, data: { [key]: number } }
  try {
    if (payload && typeof payload === "object") {
      if ("data" in payload && payload.data && typeof payload.data === "object") {
        const v = payload.data[key];
        return typeof v === "number" ? v : 0;
      }
      // If backend returns plain number in future
      if (typeof payload[key] === "number") return payload[key];
    }
  } catch {}
  return 0;
}

export const dashboardApi = {
  getChatbotSessionsCount: async (): Promise<number> => {
    const res = await api.get("/chatbot/session/");
    return extractWrappedNumber(res.data, "sessions_count");
  },
  getReportCount: async (): Promise<number> => {
    const res = await api.get("/reports/report_count");
    return extractWrappedNumber(res.data, "report_count");
  },
  getCompanyCount: async (): Promise<number> => {
    const res = await api.get("/companies/company_count/");
    return extractWrappedNumber(res.data, "company_count");
  },
  getAssetAnalysisCount: async (): Promise<number> => {
    const res = await api.get("/assets/analysiscount/");
    return extractWrappedNumber(res.data, "asset_count");
  },
  getAllMetrics: async (): Promise<DashboardMetrics> => {
    const [chatbotSessions, reportsGenerated, companiesOnboarded, assetAnalysisCount] = await Promise.all([
      dashboardApi.getChatbotSessionsCount(),
      dashboardApi.getReportCount(),
      dashboardApi.getCompanyCount(),
      dashboardApi.getAssetAnalysisCount(),
    ]);
    return { reportsGenerated, chatbotSessions, companiesOnboarded, assetAnalysisCount };
  },
};


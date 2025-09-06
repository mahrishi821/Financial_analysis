"use client";

import React from "react";
import { TrendingUp, MessageSquare, Building, BarChart3, Activity, Users } from "lucide-react";
import { useDashboardMetrics } from "../hooks/useDashboardMetrics";

function MetricCard({ icon: Icon, title, value, color, bgColor }: { icon: any; title: string; value: number; color: string; bgColor: string; }) {
  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${bgColor}`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
        <div className="flex items-center space-x-1">
          <TrendingUp className="w-4 h-4 text-green-500" />
          <span className="text-sm text-green-500 font-medium">+12%</span>
        </div>
      </div>
      <h3 className="text-gray-600 text-sm font-medium mb-2">{title}</h3>
      <p className="text-3xl font-bold text-gray-900">{value.toLocaleString()}</p>
    </div>
  );
}

export default function DashboardOverview() {
  const { data, loading, error } = useDashboardMetrics();

  if (loading) return <div className="p-6">Loading dashboard…</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (!data) return null;

  return (
    <div className="min-h-[40vh]">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard Overview</h1>
        <p className="text-gray-600">Real-time insights and analytics for your business</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          icon={BarChart3}
          title="Reports Generated"
          value={data.reportsGenerated}
          color="text-blue-600"
          bgColor="bg-blue-100"
        />
        <MetricCard
          icon={MessageSquare}
          title="Chatbot Sessions"
          value={data.chatbotSessions}
          color="text-green-600"
          bgColor="bg-green-100"
        />
        <MetricCard
          icon={Building}
          title="Companies Onboarded"
          value={data.companiesOnboarded}
          color="text-purple-600"
          bgColor="bg-purple-100"
        />
        <MetricCard
          icon={Activity}
          title="Asset Analysis Count"
          value={data.assetAnalysisCount}
          color="text-orange-600"
          bgColor="bg-orange-100"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Users className="w-5 h-5 mr-2 text-blue-600" />
            Quick Statistics
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg. Session Duration</span>
              <span className="font-semibold text-gray-900">4m 32s</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Success Rate</span>
              <span className="font-semibold text-green-600">94.2%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active Users Today</span>
              <span className="font-semibold text-blue-600">247</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-green-600" />
            System Status
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">API Response Time</span>
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">120ms</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Server Uptime</span>
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">99.9%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Data Sync</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">Real-time</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


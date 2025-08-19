"use client";
import React, { useState } from "react";
import Input from "@/components/common/Input";
import Select from "@/components/common/Select";
import Button from "@/components/common/Button";
import { CheckCircle, Building, Users } from "lucide-react";
import { useOnboarding } from "../hooks/useOnboarding";

const OnboardingForm: React.FC = () => {
  const [form, setForm] = useState({
    company_name: "",
    sector: "",
    sub_sector: "",
    country: "",
    incorporation_date: "",
    contact_person_name: "",
    contact_email: "",
    phone: "",
    frequency: "",
    status: "Active",
  });
  const { submit, loading } = useOnboarding();

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submit(form);
    alert("Company onboarded successfully!");
    setForm({
      company_name: "",
      sector: "",
      sub_sector: "",
      country: "",
      incorporation_date: "",
      contact_person_name: "",
      contact_email: "",
      phone: "",
      frequency: "",
      status: "Active",
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Company Onboarding</h2>
        <p className="text-gray-600">Add a new company to the platform.</p>
      </div>

      <form onSubmit={onSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200 flex items-center">
          <Building className="w-5 h-5 mr-2 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Company Information</h3>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input name="company_name" value={form.company_name} onChange={onChange} label="Company Name *" placeholder="Enter legal company name" required />
            <Select name="sector" value={form.sector} onChange={onChange} label="Sector *" required>
              <option value="">Select sector</option>
              {["SaaS","Fintech","Biotech","E-commerce","AI/ML","Healthcare","EdTech","Other"].map(s => <option key={s} value={s}>{s}</option>)}
            </Select>
            <Input name="sub_sector" value={form.sub_sector} onChange={onChange} label="Sub-sector" placeholder="More specific category" />
            <Select name="country" value={form.country} onChange={onChange} label="Country *" required>
              <option value="">Select country</option>
              {["United States","United Kingdom","Canada","Germany","France","Singapore","India","Other"].map(c => <option key={c} value={c}>{c}</option>)}
            </Select>
            <Input name="incorporation_date" value={form.incorporation_date} onChange={onChange} type="date" label="Incorporation Date *" required />
            <Select name="frequency" value={form.frequency} onChange={onChange} label="Reporting Frequency *" required>
              {["","Quarterly","Semi-Annual","Annual"].map(f => <option key={f || 'blank'} value={f}>{f || "Select frequency"}</option>)}
            </Select>
          </div>

          <div className="border-t border-gray-200 pt-6">
            <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2 text-blue-600" />
              Contact Information
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Input name="contact_person_name" value={form.contact_person_name} onChange={onChange} label="Contact Person *" required placeholder="Primary contact name" />
              <Input name="contact_email" value={form.contact_email} onChange={onChange} type="email" label="Contact Email *" required placeholder="contact@company.com" />
              <Input name="phone" value={form.phone} onChange={onChange} label="Phone Number" placeholder="+1 (555) 123-4567" />
              <Select name="status" value={form.status} onChange={onChange} label="Status *" required>
                {["Active","Inactive","Offboarded"].map(s => <option key={s} value={s}>{s}</option>)}
              </Select>
            </div>
          </div>

          <div className="flex justify-end pt-6 border-t border-gray-200">
            <Button type="submit" loading={loading} className="bg-blue-600 text-white hover:bg-blue-700 flex items-center">
              <CheckCircle className="w-5 h-5 mr-2" />
              Onboard Company
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default OnboardingForm;

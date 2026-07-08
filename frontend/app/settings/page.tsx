"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { Card } from '@/components/ui/components';

export default function SettingsPage() {
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      <Card>System settings configuration here.</Card>
    </DashboardLayout>
  );
}

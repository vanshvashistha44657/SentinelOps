"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/useAuthStore';
import { Card } from '@/components/ui/components';

export default function ProfilePage() {
  const user = useAuthStore((state) => state.user);
  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      <Card>
        <p>Full Name: {user?.full_name || 'N/A'}</p>
        <p>Email: {user?.email || 'N/A'}</p>
      </Card>
    </DashboardLayout>
  );
}

"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useAuthStore } from '@/store/useAuthStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export default function ProfilePage() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-6">User Profile</h1>
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>Account Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-white font-bold text-xl">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <p className="font-bold text-lg">{user?.full_name || 'N/A'}</p>
              <p className="text-muted-foreground">{user?.email || 'N/A'}</p>
            </div>
          </div>
          <p>Role: <span className="font-semibold">{user?.role?.name || 'N/A'}</span></p>
          <div className="flex gap-2">
            <Button variant="outline">Change Password</Button>
            <Button variant="destructive" onClick={handleLogout}>Logout</Button>
          </div>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}

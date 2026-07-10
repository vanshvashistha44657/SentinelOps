"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { useAuthStore } from '@/store/useAuthStore';
import { Save, Bell, Shield, User } from 'lucide-react';

export default function SettingsPage() {
  const { user, setAuth } = useAuthStore();
  
  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    // Implementation would connect to /profile/update API
    console.log('Profile updated');
  };

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Settings</h1>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User size={16} /> Profile
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Shield size={16} /> Security
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell size={16} /> Alerts
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-4">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your personal details and display preferences.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSaveProfile} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Full Name</Label>
                    <Input defaultValue={user?.full_name} placeholder="John Doe" />
                  </div>
                  <div className="space-y-2">
                    <Label>Email Address</Label>
                    <Input defaultValue={user?.email} disabled className="bg-background/50" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Job Title</Label>
                  <Input placeholder="SOC Analyst" />
                </div>
                <Button type="submit" className="flex items-center gap-2">
                  <Save size={16} /> Save Changes
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>Manage your password and session security.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-background/50 rounded-lg border border-border">
                  <div>
                    <p className="font-medium">Two-Factor Authentication</p>
                    <p className="text-sm text-text-secondary">Add an extra layer of security to your account.</p>
                  </div>
                  <Button variant="outline">Enable</Button>
                </div>
                <div className="flex items-center justify-between p-4 bg-background/50 rounded-lg border border-border">
                  <div>
                    <p className="font-medium">Password Rotation</p>
                    <p className="text-sm text-text-secondary">Set a policy for mandatory password changes.</p>
                  </div>
                  <Button variant="outline">Configure</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Control how you receive security alerts.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-background/50 rounded-lg border border-border">
                <div>
                  <p className="font-medium">Critical Alerts</p>
                  <p className="text-sm text-text-secondary">Notify immediately for critical severity alerts.</p>
                </div>
                <Input type="checkbox" className="w-5 h-5" defaultChecked />
              </div>
              <div className="flex items-center justify-between p-4 bg-background/50 rounded-lg border border-border">
                <div>
                  <p className="font-medium">Weekly Reports</p>
                  <p className="text-sm text-text-secondary">Receive a summary of security metrics every Monday.</p>
                </div>
                <Input type="checkbox" className="w-5 h-5" defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}

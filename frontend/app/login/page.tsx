"use client";
import { useState } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Eye, EyeOff, Loader2, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormMessage } from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const formSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const setAuth = useAuthStore((state) => state.setAuth);
  const router = useRouter();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      const res = await api.post('/auth/login', {
        email: values.email,
        password: values.password
      });
      // Fetch user profile separately after successful login
      const userRes = await api.get('/auth/profile', {
          headers: { Authorization: `Bearer ${res.data.access_token}` }
      });
      setAuth(res.data.access_token, userRes.data);
      router.push('/');
    } catch (error) {
      console.error('Login failed', error);
      form.setError('password', { message: 'Invalid credentials' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-background relative overflow-hidden">
      {/* Animated background element */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-primary/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-critical/10 rounded-full blur-3xl animate-pulse delay-1000" />

      <Card className="w-[400px] bg-card/50 backdrop-blur-md border-border">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <ShieldCheck className="h-12 w-12 text-primary" />
          </div>
          <CardTitle className="text-2xl font-bold">SentinelOps</CardTitle>
          <CardDescription>Enter your credentials to access the SOC</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Input placeholder="Email" {...field} className="bg-background/50" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <div className="relative">
                      <FormControl>
                        <Input 
                          type={showPassword ? 'text' : 'password'} 
                          placeholder="Password" 
                          {...field} 
                          className="bg-background/50 pr-10" 
                        />
                      </FormControl>
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-2.5 text-text-secondary"
                      >
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 'Login'}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}

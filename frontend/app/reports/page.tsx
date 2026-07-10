"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useReports } from '@/hooks/useData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FileText, Download, BarChart3 } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const MOCK_TREND_DATA = [
  { name: 'Mon', alerts: 40, incidents: 10 },
  { name: 'Tue', alerts: 30, incidents: 5 },
  { name: 'Wed', alerts: 60, incidents: 15 },
  { name: 'Thu', alerts: 45, incidents: 8 },
  { name: 'Fri', alerts: 70, incidents: 12 },
  { name: 'Sat', alerts: 20, incidents: 3 },
  { name: 'Sun', alerts: 15, incidents: 2 },
];

export default function ReportsPage() {
  const { data: reports, isLoading } = useReports();

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Reports & Analytics</h1>
        <Button className="flex items-center gap-2">
          <FileText size={18} /> Generate Report
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 size={20} /> Alert Trend (Weekly)
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MOCK_TREND_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Bar dataKey="alerts" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="incidents" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Quick Metrics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-background/50 rounded-lg border border-border">
              <span className="text-text-secondary">Mean Time to Detect (MTTD)</span>
              <span className="font-bold">4.2 hrs</span>
            </div>
            <div className="flex justify-between items-center p-4 bg-background/50 rounded-lg border border-border">
              <span className="text-text-secondary">Mean Time to Respond (MTTR)</span>
              <span className="font-bold">1.8 hrs</span>
            </div>
            <div className="flex justify-between items-center p-4 bg-background/50 rounded-lg border border-border">
              <span className="text-text-secondary">SLA Compliance Rate</span>
              <span className="font-bold text-success">94.5%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Generated Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Report Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Date Generated</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reports?.map((r: any) => (
                <TableRow key={r.id}>
                  <TableCell className="font-medium">{r.title}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{r.type}</Badge>
                  </TableCell>
                  <TableCell>{r.created_at || 'N/A'}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" className="flex items-center gap-2">
                      <Download size={16} /> PDF
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {(!reports || reports.length === 0) && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8 text-text-secondary">
                    No reports generated yet.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}

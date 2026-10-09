"use client";

import DashboardLayout from "@/components/DashboardLayout";
import { useReports } from "@/hooks/useData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, FileText } from "lucide-react";
import { useAuthStore } from "@/store/useAuthStore";

export default function ReportsPage() {
  const { data: reports, isLoading, isError } = useReports();
  const token = useAuthStore((state) => state.token);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

  const download = async (format: "excel" | "pdf") => {
    const response = await fetch(`${apiUrl}/reports/export/${format}`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
    if (!response.ok) return;
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `sentinelops-report.${format === "excel" ? "xlsx" : "pdf"}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) return <DashboardLayout>Loading reports…</DashboardLayout>;

  return <DashboardLayout>
    <div className="flex flex-col gap-6">
      <header className="flex flex-wrap justify-between gap-4 items-center">
        <div><h1 className="text-2xl font-bold">Reports & Analytics</h1><p className="text-sm text-text-secondary">Exports are generated from persisted SentinelOps records.</p></div>
        <div className="flex gap-2"><Button variant="outline" onClick={() => download("excel")}><Download size={16} /> Excel</Button><Button onClick={() => download("pdf")}><FileText size={16} /> PDF</Button></div>
      </header>
      {isError && <Card><CardContent className="text-critical">Reports could not be loaded.</CardContent></Card>}
      <Card className="bg-card border-border"><CardHeader><CardTitle>Generated Reports</CardTitle></CardHeader><CardContent>
        {reports?.length ? <div className="space-y-3">{reports.map((report: any) => <div key={report.id} className="flex flex-wrap justify-between gap-3 border-b border-border pb-3"><div><p className="font-medium">{report.title}</p><p className="text-xs text-text-secondary">{report.type} · {report.format} · {new Date(report.created_at).toLocaleString()}</p></div><span className="text-xs text-text-muted">{report.file_path || "Generated record"}</span></div>)}</div> : <p className="text-sm text-text-secondary">No reports generated yet.</p>}
      </CardContent></Card>
    </div>
  </DashboardLayout>;
}

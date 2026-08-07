"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useThreatIndicators } from '@/hooks/useData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Globe, ShieldAlert, Bug, Activity } from 'lucide-react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';

export default function ThreatIntelPage() {
  const { data: intel, isLoading } = useThreatIndicators();

  const columns = [
    { accessorKey: 'value', header: 'Indicator', cell: ({ row }: any) => <span className="font-mono text-xs">{row.getValue('value')}</span> },
    { accessorKey: 'type', header: 'Type', cell: ({ row }: any) => <Badge variant="outline">{row.getValue('type')}</Badge> },
    { accessorKey: 'source', header: 'Source' },
    { accessorKey: 'confidence', header: 'Confidence', cell: ({ row }: any) => <span className="text-text-secondary">{row.getValue('confidence')}%</span> },
  ];

  const table = useReactTable({
    data: intel || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  const summary = [
    { title: "Active Campaigns", value: "12", icon: Globe, color: "text-primary" },
    { title: "APT Groups", value: "8", icon: ShieldAlert, color: "text-warning" },
    { title: "Malware Families", value: "45", icon: Bug, color: "text-critical" },
    { title: "Threat Feeds", value: "24", icon: Activity, color: "text-success" },
  ];

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold mb-6">Threat Intelligence</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {summary.map((item) => (
          <Card key={item.title} className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-text-secondary">{item.title}</CardTitle>
              <item.icon className={`h-4 w-4 ${item.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{item.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Latest Intelligence Feed</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map(headerGroup => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map(header => (
                    <TableHead key={header.id}>
                      {flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows.map(row => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map(cell => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}

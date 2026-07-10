"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Search, Plus, Server } from 'lucide-react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';

export default function AssetsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const { data: assets, isLoading } = useQuery({ queryKey: ['assets'], queryFn: () => api.get('/assets/').then(res => res.data) });

  const columns = [
    { accessorKey: 'name', header: 'Hostname', cell: ({ row }: any) => <span className="font-medium">{row.getValue('name')}</span> },
    { accessorKey: 'ip_address', header: 'IP Address', cell: ({ row }: any) => <span className="font-mono text-xs">{row.getValue('ip_address')}</span> },
    { accessorKey: 'os', header: 'Operating System' },
    { accessorKey: 'status', header: 'Status', cell: ({ row }: any) => <Badge variant="outline">{row.getValue('status')}</Badge> },
    { accessorKey: 'risk_score', header: 'Risk Score', cell: ({ row }: any) => (
      <Badge variant={row.getValue('risk_score') > 70 ? 'destructive' : 'default'}>
        {row.getValue('risk_score')}
      </Badge>
    )},
  ];

  const table = useReactTable({
    data: assets || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Asset Management</h1>
        <Button className="flex items-center gap-2">
          <Plus size={18} /> Add Asset
        </Button>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 text-text-secondary" size={18} />
          <input 
            type="text" 
            placeholder="Search assets..." 
            className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <Card className="bg-card border-border">
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
      </Card>
    </DashboardLayout>
  );
}


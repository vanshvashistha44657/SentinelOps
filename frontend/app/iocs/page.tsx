"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useIOCs } from '@/hooks/useData';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Plus, Download, Upload, Search } from 'lucide-react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';

export default function IOCsPage() {
  const { data: iocs, isLoading } = useIOCs();
  const [searchQuery, setSearchQuery] = useState('');

  const columns = [
    { accessorKey: 'value', header: 'Indicator Value', cell: ({ row }: any) => <span className="font-mono text-xs">{row.getValue('value')}</span> },
    { accessorKey: 'type', header: 'Type', cell: ({ row }: any) => <Badge variant="outline">{row.getValue('type')}</Badge> },
    { accessorKey: 'confidence', header: 'Confidence', cell: ({ row }: any) => <span className="text-text-secondary">{row.getValue('confidence')}%</span> },
    { accessorKey: 'source', header: 'Source' },
    { accessorKey: 'expiration', header: 'Expires' },
  ];

  const table = useReactTable({
    data: iocs || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">IOC Management</h1>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Upload size={16} /> Import
          </Button>
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Download size={16} /> Export
          </Button>
          <Button className="flex items-center gap-2">
            <Plus size={16} /> Add IOC
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 text-text-secondary" size={18} />
          <input 
            type="text" 
            placeholder="Search indicators..." 
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

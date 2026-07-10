"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAlerts } from '@/hooks/useData';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';

export default function AlertsPage() {
  const { data: alerts, isLoading } = useAlerts();
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns: ColumnDef<any>[] = [
    { accessorKey: 'severity', header: 'Severity', cell: ({ row }) => (
      <Badge variant={row.getValue('severity') === 'CRITICAL' ? 'destructive' : 'default'}>
        {row.getValue('severity')}
      </Badge>
    )},
    { accessorKey: 'title', header: 'Alert Title' },
    { accessorKey: 'status', header: 'Status' },
    { accessorKey: 'time', header: 'Time' },
  ];

  const table = useReactTable({
    data: alerts || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: { sorting },
  });

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold mb-6">Alerts</h1>
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

"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useCases } from '@/hooks/useData';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';

export default function CasesPage() {
  const { data: cases, isLoading } = useCases();

  const columns = [
    { accessorKey: 'id', header: 'ID' },
    { accessorKey: 'title', header: 'Case Title' },
    { accessorKey: 'status', header: 'Status', cell: ({ row }: any) => <Badge variant="outline">{row.getValue('status')}</Badge> },
    { accessorKey: 'priority', header: 'Priority' },
  ];

  const table = useReactTable({
    data: cases || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold mb-6">Cases</h1>
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

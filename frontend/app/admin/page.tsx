"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useAdminUsers } from '@/hooks/useData';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { UserPlus, ShieldCheck, Key } from 'lucide-react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';

export default function AdminPage() {
  const { data: users, isLoading } = useAdminUsers();

  const columns = [
    { accessorKey: 'full_name', header: 'Full Name' },
    { accessorKey: 'email', header: 'Email' },
    { accessorKey: 'role', header: 'Role', cell: ({ row }: any) => <Badge variant="outline">{row.getValue('role')}</Badge> },
    { accessorKey: 'last_login', header: 'Last Login' },
    { 
      id: 'actions', 
      header: 'Actions', 
      cell: ({ row }: any) => (
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" className="flex items-center gap-1">
            <ShieldCheck size={14} /> Permissions
          </Button>
          <Button variant="ghost" size="sm" className="flex items-center gap-1">
            <Key size={14} /> Reset
          </Button>
        </div>
      ) 
    },
  ];

  const table = useReactTable({
    data: users || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Admin Panel</h1>
        <Button className="flex items-center gap-2">
          <UserPlus size={18} /> Invite User
        </Button>
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

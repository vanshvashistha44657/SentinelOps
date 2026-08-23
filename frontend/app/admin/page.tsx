"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useAdminUsers, useApproveUser, useRejectUser } from '@/hooks/useData';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { UserPlus, ShieldCheck, Key, CheckCircle, XCircle } from 'lucide-react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  createColumnHelper,
} from '@tanstack/react-table';

const columnHelper = createColumnHelper<any>();

export default function AdminPage() {
  const { data: users, isLoading } = useAdminUsers();
  const approveUser = useApproveUser();
  const rejectUser = useRejectUser();

  const allUsers = users || [];
  const pendingUsers = allUsers.filter((u: any) => u.approval_status === 'PENDING');
  const activeUsers = allUsers.filter((u: any) => u.last_seen_at && new Date(u.last_seen_at).getTime() > Date.now() - 300000);

  const commonColumns = [
    columnHelper.accessor('full_name', { header: 'Full Name' }),
    columnHelper.accessor('email', { header: 'Email' }),
    columnHelper.accessor('role', { header: 'Role', cell: (info) => <Badge variant="outline">{info.getValue()}</Badge> }),
    columnHelper.accessor('approval_status', { header: 'Status' }),
  ];

  const activeColumns = [
    ...commonColumns,
    columnHelper.accessor('last_seen_at', { header: 'Last Seen', cell: (info) => new Date(info.getValue() as string).toLocaleString() }),
  ];

  const allTable = useReactTable({ data: allUsers, columns: allUsersColumns, getCoreRowModel: getCoreRowModel() });
  const pendingTable = useReactTable({ data: pendingUsers, columns: pendingColumns, getCoreRowModel: getCoreRowModel() });
  const activeTable = useReactTable({ data: activeUsers, columns: activeColumns, getCoreRowModel: getCoreRowModel() });

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Admin Panel</h1>
        <Button className="flex items-center gap-2">
          <UserPlus size={18} /> Invite User
        </Button>
      </div>

      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">All Users</TabsTrigger>
          <TabsTrigger value="pending">
            Pending Approvals ({pendingUsers.length})
          </TabsTrigger>
          <TabsTrigger value="active">Active Users ({activeUsers.length})</TabsTrigger>
        </TabsList>
        <TabsContent value="all">
          <Card className="bg-card border-border">
            <Table>
              <TableHeader>
                {allTable.getHeaderGroups().map(hg => (
                  <TableRow key={hg.id}>{hg.headers.map(h => <TableHead key={h.id}>{flexRender(h.column.columnDef.header, h.getContext())}</TableHead>)}</TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {allTable.getRowModel().rows.map(r => (
                  <TableRow key={r.id}>{r.getVisibleCells().map(c => <TableCell key={c.id}>{flexRender(c.column.columnDef.cell, c.getContext())}</TableCell>)}</TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
        <TabsContent value="pending">
          <Card className="bg-card border-border">
            <Table>
              <TableHeader>
                {pendingTable.getHeaderGroups().map(hg => (
                  <TableRow key={hg.id}>{hg.headers.map(h => <TableHead key={h.id}>{flexRender(h.column.columnDef.header, h.getContext())}</TableHead>)}</TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {pendingTable.getRowModel().rows.map(r => (
                  <TableRow key={r.id}>{r.getVisibleCells().map(c => <TableCell key={c.id}>{flexRender(c.column.columnDef.cell, c.getContext())}</TableCell>)}</TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
        <TabsContent value="active">
          <Card className="bg-card border-border">
            <Table>
              <TableHeader>
                {activeTable.getHeaderGroups().map(hg => (
                  <TableRow key={hg.id}>{hg.headers.map(h => <TableHead key={h.id}>{flexRender(h.column.columnDef.header, h.getContext())}</TableHead>)}</TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {activeTable.getRowModel().rows.map(r => (
                  <TableRow key={r.id}>{r.getVisibleCells().map(c => <TableCell key={c.id}>{flexRender(c.column.columnDef.cell, c.getContext())}</TableCell>)}</TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}

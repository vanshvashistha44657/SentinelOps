"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useIncidents } from '@/hooks/useData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

export default function IncidentsPage() {
  const { data: incidents, isLoading } = useIncidents();

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold mb-6">Incidents</h1>
      
      <Tabs defaultValue="table" className="space-y-4">
        <TabsList>
          <TabsTrigger value="table">Table View</TabsTrigger>
          <TabsTrigger value="kanban">Kanban View</TabsTrigger>
        </TabsList>
        
        <TabsContent value="table">
          <Card className="bg-card border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Owner</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidents?.map((inc: any) => (
                  <TableRow key={inc.id}>
                    <TableCell>{inc.id}</TableCell>
                    <TableCell className="font-medium">{inc.title}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{inc.status}</Badge>
                    </TableCell>
                    <TableCell>{inc.owner || 'Unassigned'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="kanban">
          <div className="grid grid-cols-4 gap-4">
            {['OPEN', 'INVESTIGATING', 'CONTAINED', 'CLOSED'].map(status => (
              <div key={status} className="space-y-4">
                <h3 className="font-semibold text-text-secondary">{status}</h3>
                {incidents?.filter((i: any) => i.status === status).map((inc: any) => (
                  <Card key={inc.id} className="p-4 bg-card border-border">
                    <CardTitle className="text-sm">{inc.title}</CardTitle>
                  </Card>
                ))}
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
}

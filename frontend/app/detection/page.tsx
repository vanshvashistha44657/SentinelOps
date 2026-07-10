"use client";
import DashboardLayout from '@/components/DashboardLayout';
import { useDetectionRules } from '@/hooks/useData';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Plus, Play, Trash2 } from 'lucide-react';

export default function DetectionRulesPage() {
  const { data: rules, isLoading } = useDetectionRules();

  if (isLoading) return <DashboardLayout>Loading...</DashboardLayout>;

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Detection Rules</h1>
        <Button className="flex items-center gap-2">
          <Plus size={18} /> Create Rule
        </Button>
      </div>
      
      <Card className="bg-card border-border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Rule Name</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>MITRE Technique</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rules?.map((rule: any) => (
              <TableRow key={rule.id}>
                <TableCell className="font-medium">{rule.name}</TableCell>
                <TableCell>
                  <Badge variant={rule.severity === 'CRITICAL' ? 'destructive' : 'default'}>
                    {rule.severity}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{rule.enabled ? 'Enabled' : 'Disabled'}</Badge>
                </TableCell>
                <TableCell>{rule.mitre_technique || 'N/A'}</TableCell>
                <TableCell className="text-right space-x-2">
                  <Button variant="ghost" size="icon"><Play size={16} /></Button>
                  <Button variant="ghost" size="icon" className="text-critical"><Trash2 size={16} /></Button>
                </TableCell>
              </TableRow>
            ))}
            {(!rules || rules.length === 0) && (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-text-secondary">
                  No detection rules found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </DashboardLayout>
  );
}

"use client";
import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useThreatHunting } from '@/hooks/useData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

export default function HuntingPage() {
  const [query, setQuery] = useState('');
  const { data: results, isLoading } = useThreatHunting();

  return (
    <DashboardLayout>
      <h1 className="text-2xl font-bold mb-6">Threat Hunting</h1>
      
      <Card className="mb-6 bg-card border-border">
        <CardHeader>
          <CardTitle>Query Editor</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea 
            placeholder="Enter hunting query (e.g., SELECT * FROM logs WHERE ...)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="bg-background/50 font-mono"
          />
          <Button>Execute Query</Button>
        </CardContent>
      </Card>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Results</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Running query...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Query String</TableHead>
                  <TableHead>Timestamp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {results?.map((q: any) => (
                  <TableRow key={q.id}>
                    <TableCell className="font-mono">{q.query_string}</TableCell>
                    <TableCell>{q.created_at || 'N/A'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}

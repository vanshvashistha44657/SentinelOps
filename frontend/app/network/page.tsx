"use client";

import DashboardLayout from "@/components/DashboardLayout";
import { SOCBadge, SOCCard, SOCCardContent, SOCCardHeader, SOCTable } from "@/components/soc-ui";
import { useNetworkDevices, useNetworkHealth, useNetworkInterfaces, useNetworkOverview } from "@/hooks/useData";
import { Activity, Cable, CircleAlert, Globe2, Router, Wifi } from "lucide-react";

function value(value: unknown) {
  return value === null || value === undefined || value === "" ? "Unavailable" : String(value);
}

function statusVariant(status: string) {
  if (["PASS", "CONNECTED", "ONLINE", "ACTIVE"].includes(status)) return "success" as const;
  if (["FAIL", "OFFLINE", "DISCONNECTED", "REVOKED"].includes(status)) return "critical" as const;
  return "warning" as const;
}

export default function NetworkPage() {
  const overview = useNetworkOverview();
  const devices = useNetworkDevices({ page: 1, size: 100 });
  const interfaces = useNetworkInterfaces();
  const health = useNetworkHealth();

  if ([overview, devices, interfaces, health].some((query) => query.isLoading)) {
    return <DashboardLayout><div className="text-text-secondary">Loading network telemetry…</div></DashboardLayout>;
  }

  const snapshot = overview.data?.snapshot;
  const sensor = overview.data?.sensor;
  const latestHealth = health.data?.slice(0, 4) || [];

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Network Intelligence</h1>
          <p className="text-text-secondary text-sm">Authorized host telemetry, bounded diagnostics, and observed local devices</p>
        </header>

        {overview.isError || devices.isError || interfaces.isError || health.isError ? (
          <SOCCard><SOCCardContent className="text-critical">Network telemetry is currently unavailable. Check sensor and API connectivity.</SOCCardContent></SOCCard>
        ) : null}

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <SOCCard><SOCCardHeader title="Connection" /><SOCCardContent><div className="flex items-center gap-2"><Wifi size={18} /><SOCBadge variant={statusVariant(value(snapshot?.connection_status))}>{value(snapshot?.connection_status)}</SOCBadge></div><p className="mt-2 text-sm text-text-secondary">{value(snapshot?.connection_type)}</p></SOCCardContent></SOCCard>
          <SOCCard><SOCCardHeader title="Gateway" /><SOCCardContent><div className="flex items-center gap-2"><Router size={18} /><span className="font-mono text-sm">{value(snapshot?.gateway)}</span></div><p className="mt-2 text-xs text-text-muted">Reachability comes from the sensor’s last bounded check.</p></SOCCardContent></SOCCard>
          <SOCCard><SOCCardHeader title="Observed Devices" /><SOCCardContent><div className="flex items-center gap-2"><Globe2 size={18} /><span className="text-2xl font-bold">{value(overview.data?.device_count)}</span></div><p className="mt-2 text-sm text-text-secondary">{value(overview.data?.online_device_count)} currently online</p></SOCCardContent></SOCCard>
          <SOCCard><SOCCardHeader title="Sensor Freshness" /><SOCCardContent><div className="flex items-center gap-2"><Activity size={18} /><SOCBadge variant={statusVariant(value(sensor?.status))}>{value(sensor?.status)}</SOCBadge></div><p className="mt-2 text-xs text-text-muted">Last telemetry: {sensor?.last_telemetry_at ? new Date(sensor.last_telemetry_at).toLocaleString() : "Unavailable"}</p></SOCCardContent></SOCCard>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <SOCCard><SOCCardHeader title="Current Network Snapshot" /><SOCCardContent className="grid grid-cols-2 gap-4 text-sm">
            <div><p className="text-xs text-text-muted">SSID</p><p>{value(snapshot?.ssid)}</p></div>
            <div><p className="text-xs text-text-muted">BSSID</p><p className="font-mono">{value(snapshot?.bssid)}</p></div>
            <div><p className="text-xs text-text-muted">Local IPv4</p><p className="font-mono">{value(snapshot?.local_ipv4?.join(", "))}</p></div>
            <div><p className="text-xs text-text-muted">DNS</p><p className="font-mono">{value(snapshot?.dns_servers?.join(", "))}</p></div>
            <div><p className="text-xs text-text-muted">Wi-Fi band / channel</p><p>{value(snapshot?.wifi_band)} / {value(snapshot?.channel)}</p></div>
            <div><p className="text-xs text-text-muted">Security</p><p>{value(snapshot?.security_protocol)}</p></div>
          </SOCCardContent></SOCCard>
          <SOCCard><SOCCardHeader title="Latest Diagnostics" /><SOCCardContent className="space-y-3">
            {latestHealth.length === 0 ? <p className="text-sm text-text-muted">No health measurements received.</p> : latestHealth.map((item: any) => <div key={item.id} className="flex items-center justify-between border-b border-border pb-2"><div><p className="text-sm">{item.check_type}</p><p className="text-xs text-text-muted">{value(item.target)} · {item.measured_at ? new Date(item.measured_at).toLocaleString() : "Unavailable"}</p></div><SOCBadge variant={statusVariant(item.status)}>{item.status}</SOCBadge></div>)}
          </SOCCardContent></SOCCard>
        </div>

        <SOCCard><SOCCardHeader title="Network Interface Inventory" /><SOCCardContent className="p-0"><SOCTable headers={[{ label: "Interface", accessor: "name" }, { label: "Type", accessor: "interface_type" }, { label: "State", accessor: "operational_state" }, { label: "Addresses", accessor: "ipv4_addresses" }, { label: "MAC", accessor: "mac_address" }]} data={interfaces.data || []} renderCell={(item: any, column: string) => column === "operational_state" ? <SOCBadge variant={statusVariant(item[column])}>{item[column]}</SOCBadge> : column === "ipv4_addresses" ? <span className="font-mono text-xs">{value(item[column]?.join(", "))}</span> : value(item[column])} /></SOCCardContent></SOCCard>

        <SOCCard><SOCCardHeader title="Observed Device Inventory" /><SOCCardContent className="p-0"><SOCTable headers={[{ label: "IP", accessor: "ip_address" }, { label: "MAC", accessor: "mac_address" }, { label: "Hostname", accessor: "hostname" }, { label: "Vendor estimate", accessor: "vendor" }, { label: "Status", accessor: "status" }, { label: "Last seen", accessor: "last_seen" }]} data={devices.data || []} renderCell={(item: any, column: string) => column === "status" ? <SOCBadge variant={statusVariant(item[column])}>{item[column]}</SOCBadge> : column === "last_seen" ? new Date(item[column]).toLocaleString() : value(item[column])} /></SOCCardContent></SOCCard>

        <div className="flex gap-2 text-xs text-text-muted"><CircleAlert size={15} /><span>{overview.data?.limitations?.join(" ") || "Visibility depends on the sensor OS, permissions, topology, and neighbor-table evidence."}</span></div>
      </div>
    </DashboardLayout>
  );
}

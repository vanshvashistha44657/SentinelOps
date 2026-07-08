export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 p-4">
      <h2 className="text-xl font-bold mb-6">SentinelOps</h2>
      <nav className="space-y-2">
        <a href="/" className="block p-2 hover:bg-slate-800 rounded">Dashboard</a>
        <a href="/alerts" className="block p-2 hover:bg-slate-800 rounded">Alerts</a>
        <a href="/incidents" className="block p-2 hover:bg-slate-800 rounded">Incidents</a>
        <a href="/cases" className="block p-2 hover:bg-slate-800 rounded">Cases</a>
        <a href="/hunting" className="block p-2 hover:bg-slate-800 rounded">Threat Hunting</a>
        <a href="/iocs" className="block p-2 hover:bg-slate-800 rounded">IOCs</a>
        <a href="/threat-intel" className="block p-2 hover:bg-slate-800 rounded">Threat Intel</a>
        <a href="/assets" className="block p-2 hover:bg-slate-800 rounded">Assets</a>
        <a href="/reports" className="block p-2 hover:bg-slate-800 rounded">Reports</a>
        <a href="/admin" className="block p-2 hover:bg-slate-800 rounded">Admin</a>
        <a href="/profile" className="block p-2 hover:bg-slate-800 rounded">Profile</a>
        <a href="/settings" className="block p-2 hover:bg-slate-800 rounded">Settings</a>
      </nav>
    </aside>
  );
}

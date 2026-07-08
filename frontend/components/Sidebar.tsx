export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 p-4">
      <h2 className="text-xl font-bold mb-6">SentinelOps</h2>
      <nav className="space-y-2">
        <a href="/" className="block p-2 hover:bg-slate-800 rounded">Dashboard</a>
        <a href="/alerts" className="block p-2 hover:bg-slate-800 rounded">Alerts</a>
        <a href="/incidents" className="block p-2 hover:bg-slate-800 rounded">Incidents</a>
        <a href="/cases" className="block p-2 hover:bg-slate-800 rounded">Cases</a>
      </nav>
    </aside>
  );
}

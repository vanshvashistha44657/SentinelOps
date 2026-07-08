export const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={`p-4 bg-slate-800 rounded border border-slate-700 ${className}`}>{children}</div>
);
export const Badge = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <span className={`px-2 py-1 rounded text-xs font-semibold ${className}`}>{children}</span>
);

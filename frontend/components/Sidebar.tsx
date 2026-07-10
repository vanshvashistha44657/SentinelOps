import { 
  LayoutDashboard, AlertTriangle, ShieldAlert, Briefcase, 
  Search, ShieldCheck, Target, Server, FileText, 
  Settings, User, Shield 
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const menuItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Alerts", href: "/alerts", icon: AlertTriangle },
  { name: "Incidents", href: "/incidents", icon: ShieldAlert },
  { name: "Cases", href: "/cases", icon: Briefcase },
  { name: "Threat Hunting", href: "/hunting", icon: Search },
  { name: "Detection Rules", href: "/detection", icon: ShieldCheck },
  { name: "IOC Management", href: "/iocs", icon: Target },
  { name: "Threat Intelligence", href: "/threat-intel", icon: Shield },
  { name: "Asset Management", href: "/assets", icon: Server },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Settings", href: "/settings", icon: Settings },
  { name: "Profile", href: "/profile", icon: User },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-sidebar border-r border-border p-4 flex flex-col h-screen">
      <div className="text-xl font-bold mb-8 text-primary">SentinelOps</div>
      <nav className="space-y-1 flex-1">
        {menuItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center gap-3 p-3 rounded-md text-text-secondary hover:bg-card hover:text-text-primary transition-colors",
            )}
          >
            <item.icon size={20} />
            {item.name}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

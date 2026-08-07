import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
}

export const SOCCard = ({ className, children, onClick }: CardProps) => (
  <div className={cn("soc-card", className)} onClick={onClick}>
    {children}
  </div>
);

export const SOCCardHeader = ({ children, className, title, action }: { children?: React.ReactNode; className?: string; title?: string; action?: React.ReactNode }) => (
  <div className={cn("soc-card-header", className)}>
    {title && <h3 className="text-sm font-semibold text-text-primary">{title}</h3>}
    <div className="flex items-center gap-2">
      {children}
      {action}
    </div>
  </div>
);

export const SOCCardContent = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={cn("soc-card-content", className)}>
    {children}
  </div>
);

interface TableProps<T> {
  headers: { label: string; accessor: keyof T | string }[];
  data: T[];
  className?: string;
  onRowClick?: (item: T) => void;
  renderCell?: (item: T, column: string) => React.ReactNode;
}

export function SOCTable<T>({ headers, data, className, onRowClick, renderCell }: TableProps<T>) {
  return (
    <div className={cn("overflow-x-auto", className)}>
      <table className="soc-table">
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="soc-table-header">{h.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="soc-table-row" onClick={() => onRowClick?.(row)}>
              {headers.map((h, j) => (
                <td key={j} className="soc-table-cell">
                  {renderCell ? renderCell(row, h.accessor as string) : (row[h.accessor as keyof T] as React.ReactNode)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export const SOCBadge = ({ children, variant = 'info', className }: { children: React.ReactNode; variant?: 'info' | 'success' | 'warning' | 'critical'; className?: string }) => {
  const variants = {
    info: "bg-info/20 text-info border border-info/30",
    success: "bg-success/20 text-success border border-success/30",
    warning: "bg-warning/20 text-warning border border-warning/30",
    critical: "bg-critical/20 text-critical border border-critical/30",
  };
  return (
    <span className={cn("soc-badge", variants[variant], className)}>
      {children}
    </span>
  );
};

export const SOCInput = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => (
  <input ref={ref} className={cn("soc-input", className)} {...props} />
));
SOCInput.displayName = "SOCInput";

export const SOCButton = ({ children, variant = 'primary', size, className, ...props }: { children: React.ReactNode; variant?: 'primary' | 'secondary'; size?: 'sm' | 'md' | 'xs' | 'lg'; className?: string } & React.ButtonHTMLAttributes<HTMLButtonElement>) => {
  const variants = {
    primary: "soc-btn-primary",
    secondary: "soc-btn-secondary",
  };
  return (
    <button className={cn(variants[variant], className)} {...props}>
      {children}
    </button>
  );
};

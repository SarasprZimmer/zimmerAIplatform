export function Card({ children, className="", ...props }: { children: React.ReactNode; className?: string } & React.HTMLAttributes<HTMLDivElement>) {
  return <div className={`rounded-2xl border bg-white p-4 ${className}`} {...props}>{children}</div>;
}

export function Skeleton({ className="" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-200/70 rounded-xl ${className}`} />;
}

export function Empty({ children }: { children: React.ReactNode }) {
  return <div className="text-sm opacity-70">{children}</div>;
}

export function Badge({ children, className="" }: { children: React.ReactNode; className?: string }) {
  return <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${className}`}>{children}</span>;
}
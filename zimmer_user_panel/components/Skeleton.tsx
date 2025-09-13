export function Skeleton({ className="" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-200/70 rounded-xl ${className}`} />;
}

export function Card({ children, className="", onClick, ...props }: { 
  children: React.ReactNode; 
  className?: string;
  onClick?: () => void;
  [key: string]: any;
}) {
  return <div className={`rounded-2xl border bg-white p-4 ${className}`} onClick={onClick} {...props}>{children}</div>;
}

'use client';
export default function FormattedDate({ date, locale = 'fa-IR' }: { date: string, locale?: string }) {
  return <>{new Date(date).toLocaleString(locale)}</>;
} 
"use client";
import { useEffect, useState } from "react";
export function Toast({ msg, onDone }: { msg: string; onDone?: ()=>void }) {
  const [show, setShow] = useState(true);
  useEffect(() => {
    const t = setTimeout(()=>{ setShow(false); onDone?.(); }, 2500);
    return ()=> clearTimeout(t);
  }, [onDone]);
  if (!show) return null;
  return (
    <div className="fixed bottom-4 right-4 bg-black/80 text-white rounded-xl px-4 py-2 shadow">
      {msg}
    </div>
  );
}

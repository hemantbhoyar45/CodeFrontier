"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { Check, X } from "lucide-react";

type Toast = { id: number; message: string; tone: "success" | "error" };
type ToastContextValue = { notify: (message: string, tone?: Toast["tone"]) => void };
const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const notify = useCallback((message: string, tone: Toast["tone"] = "success") => {
    const id = Date.now() + Math.random();
    setToasts((items) => [...items, { id, message, tone }]);
    window.setTimeout(
      () => setToasts((items) => items.filter((item) => item.id !== id)),
      4200,
    );
  }, []);
  const value = useMemo(() => ({ notify }), [notify]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div aria-live="polite" className="fixed bottom-5 right-5 z-[100] grid gap-2">
        {toasts.map((toast) => (
          <div
            className="flex items-center gap-3 rounded-xl border border-border bg-white px-4 py-3 text-sm shadow-lg"
            key={toast.id}
            role={toast.tone === "error" ? "alert" : "status"}
          >
            <span className={toast.tone === "success" ? "text-emerald-700" : "text-red-700"}>
              {toast.tone === "success" ? <Check size={16} /> : <X size={16} />}
            </span>
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const value = useContext(ToastContext);
  if (!value) throw new Error("useToast must be used within ToastProvider.");
  return value;
}

import type { ReactNode } from "react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return <main className="min-h-screen bg-[#f7f5f0]">{children}</main>;
}

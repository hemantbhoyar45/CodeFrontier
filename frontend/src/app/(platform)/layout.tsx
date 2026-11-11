import type { ReactNode } from "react";

export default function PlatformLayout({ children }: { children: ReactNode }) {
  return <main className="min-h-screen overflow-hidden">{children}</main>;
}

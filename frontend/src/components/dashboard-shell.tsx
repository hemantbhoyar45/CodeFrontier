"use client";

import {
  Archive,
  BookOpen,
  ChevronDown,
  CircleHelp,
  FileText,
  GitBranch,
  LayoutDashboard,
  LogOut,
  Menu,
  PanelLeftClose,
  Plug,
  Settings,
  ShieldCheck,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { AppProvider, useAppContext } from "@/components/app-provider";
import { BrandMark } from "@/components/brand-mark";
import { ToastProvider } from "@/components/toast-provider";

const navigation = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Projects", href: "/dashboard/projects", icon: GitBranch },
  { label: "Knowledge Base", href: "/dashboard/knowledge", icon: BookOpen },
  { label: "Documents", href: "/dashboard/documents", icon: FileText },
  { label: "Integrations", href: "/dashboard/integrations", icon: Plug },
  { label: "Reviews", href: "/dashboard/reviews", icon: ShieldCheck },
  { label: "Handover Reports", href: "/dashboard/handovers", icon: Archive },
  { label: "Team Members", href: "/dashboard/team", icon: Users },
  { label: "Audit Logs", href: "/dashboard/audit", icon: PanelLeftClose },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
];

function ShellContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const {
    user,
    organizations,
    organization,
    organizationRole,
    loading,
    error,
    refresh,
    selectOrganization,
    signOut,
  } = useAppContext();
  const [mobileOpen, setMobileOpen] = useState(false);

  const sidebar = (
    <aside className="flex h-full flex-col border-r border-[#e7e2d9] bg-[#fbfaf7]">
      <div className="flex h-[76px] items-center gap-3 border-b border-[#e7e2d9] px-6">
        <BrandMark />
        <span className="text-[13px] font-bold tracking-[0.16em] text-[#172b43]">KNOWBRIDGE</span>
        <button
          aria-label="Close navigation"
          className="ml-auto rounded-lg p-2 text-[#6e7781] hover:bg-[#f1eee8] lg:hidden"
          onClick={() => setMobileOpen(false)}
          type="button"
        >
          <X size={18} />
        </button>
      </div>
      <div className="px-4 pb-4 pt-5">
        <label className="mb-2 block px-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-[#99958d]">
          Workspace
        </label>
        <div className="relative">
          <select
            aria-label="Switch organization"
            className="h-11 w-full appearance-none rounded-xl border border-[#e7e2d9] bg-white pl-3 pr-9 text-left text-sm font-medium text-[#27384b] outline-none transition focus:border-[#d3a54e] focus:ring-2 focus:ring-[#d3a54e]/20"
            disabled={loading || organizations.length === 0}
            onChange={(event) => void selectOrganization(event.target.value)}
            value={organization?.id ?? ""}
          >
            {organizations.length === 0 ? (
              <option value="">No workspace yet</option>
            ) : (
              organizations.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))
            )}
          </select>
          <ChevronDown
            aria-hidden="true"
            className="pointer-events-none absolute right-3 top-3.5 text-[#89877f]"
            size={16}
          />
        </div>
        {organizations.length === 0 && !loading && (
          <Link
            className="mt-2 inline-flex items-center gap-1 px-2 text-xs font-medium text-[#9a6b1b] hover:underline"
            href="/dashboard/settings"
            onClick={() => setMobileOpen(false)}
          >
            Create an organization
          </Link>
        )}
      </div>
      <nav aria-label="Main navigation" className="flex-1 space-y-1 overflow-y-auto px-3 py-2">
        {navigation
          .filter((item) => {
            if (item.href === "/dashboard/team" || item.href === "/dashboard/settings") {
              return organizationRole !== "viewer";
            }
            if (item.href === "/dashboard/audit") {
              return organizationRole === "owner" || organizationRole === "admin";
            }
            return true;
          })
          .map(({ label, href, icon: Icon }) => {
            const active =
              href === "/dashboard"
                ? pathname === href
                : pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link
                aria-current={active ? "page" : undefined}
                className={`group flex h-10 items-center gap-3 rounded-xl px-3 text-[13px] font-medium transition-colors ${
                  active
                    ? "bg-[#182d46] text-white shadow-sm"
                    : "text-[#65717d] hover:bg-[#f0ede7] hover:text-[#20334a]"
                }`}
                href={href}
                key={href}
                onClick={() => setMobileOpen(false)}
              >
                <Icon size={17} strokeWidth={1.8} />
                {label}
              </Link>
            );
          })}
      </nav>
      <div className="border-t border-[#e7e2d9] p-4">
        <div className="mb-3 rounded-xl bg-[#f2efe8] px-3 py-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#46596a]">
            <CircleHelp size={15} className="text-[#b38635]" />
            Keep context moving
          </div>
          <p className="mt-1.5 text-[11px] leading-4 text-[#7d817f]">
            A clearer handover starts with shared knowledge.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-[#e8d8b8] text-xs font-bold text-[#604a23]">
            {user?.full_name
              .split(/\s+/)
              .map((part) => part[0])
              .slice(0, 2)
              .join("")
              .toUpperCase() ?? "KB"}
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-semibold text-[#26394d]">
              {user?.full_name ?? "Loading profile"}
            </p>
            <p className="truncate text-[11px] capitalize text-[#858982]">
              {organizationRole ?? "Workspace member"}
            </p>
          </div>
          <button
            aria-label="Sign out"
            className="rounded-lg p-2 text-[#737b80] transition hover:bg-white hover:text-[#9b3d34]"
            onClick={() => void signOut()}
            title="Sign out"
            type="button"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );

  return (
    <main className="min-h-screen bg-[#f7f5f0] text-[#1d3046]">
      <div className="min-h-screen lg:grid lg:grid-cols-[256px_minmax(0,1fr)]">
        <div className="fixed inset-y-0 left-0 z-50 hidden w-64 lg:block">{sidebar}</div>
        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <button
              aria-label="Close navigation overlay"
              className="absolute inset-0 bg-[#15283d]/35"
              onClick={() => setMobileOpen(false)}
              type="button"
            />
            <div className="relative h-full w-[min(84vw,300px)] shadow-2xl">{sidebar}</div>
          </div>
        )}
        <div className="min-w-0 lg:col-start-2">
          <header className="sticky top-0 z-30 flex h-[68px] items-center justify-between border-b border-[#e7e2d9] bg-[#fbfaf7]/95 px-5 backdrop-blur sm:px-8">
            <div className="flex items-center gap-3">
              <button
                aria-label="Open navigation"
                className="rounded-lg p-2 text-[#5b6876] hover:bg-[#f0ede7] lg:hidden"
                onClick={() => setMobileOpen(true)}
                type="button"
              >
                <Menu size={19} />
              </button>
              <div className="hidden text-[11px] text-[#9a978f] sm:block">
                Workspace <span className="px-1.5">/</span>
                <span className="font-medium text-[#5b6876]">{organization?.name ?? "Overview"}</span>
              </div>
              <span className="text-sm font-semibold text-[#26394d] sm:hidden">
                {organization?.name ?? "KNOWBRIDGE"}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="hidden rounded-full border border-[#eadcbf] bg-[#fbf6e9] px-3 py-1.5 text-[11px] font-medium text-[#927037] sm:inline-flex">
                {organizationRole ?? "Workspace"}
              </span>
              <Link
                aria-label="Profile and settings"
                className="flex size-9 items-center justify-center rounded-full border border-[#e5d8be] bg-[#eee3ce] text-xs font-bold text-[#604a23] transition hover:ring-2 hover:ring-[#d3a54e]/30"
                href="/dashboard/settings"
              >
                {user?.full_name.slice(0, 1).toUpperCase() ?? "U"}
              </Link>
            </div>
          </header>
          <div className="mx-auto max-w-[1500px] px-5 py-7 sm:px-8 lg:px-10 lg:py-9">
            {error && (
              <div
                className="mb-6 flex items-center justify-between gap-4 rounded-xl border border-[#e7c9c4] bg-[#fff9f7] px-4 py-3 text-sm text-[#8d3931]"
                role="alert"
              >
                <span>{error}</span>
                <button className="font-semibold underline" onClick={() => void refresh()}>
                  Retry
                </button>
              </div>
            )}
            {children}
          </div>
        </div>
      </div>
    </main>
  );
}

export function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <AppProvider>
      <ToastProvider>
        <ShellContent>{children}</ShellContent>
      </ToastProvider>
    </AppProvider>
  );
}

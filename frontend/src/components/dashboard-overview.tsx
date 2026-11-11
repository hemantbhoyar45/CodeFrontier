"use client";

import {
  ArrowUpRight,
  BookOpen,
  FileText,
  GitBranch,
  ShieldCheck,
  TriangleAlert,
  Users,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { useAppContext } from "@/components/app-provider";
import { apiRequest, getErrorMessage } from "@/lib/api";
import type { DashboardSummary } from "@/lib/types";

const metrics = [
  { key: "total_projects", label: "Total projects", icon: GitBranch, href: "/dashboard/projects" },
  { key: "active_projects", label: "Active projects", icon: ArrowUpRight, href: "/dashboard/projects" },
  { key: "knowledge_items", label: "Knowledge collected", icon: BookOpen, href: "/dashboard/knowledge" },
  { key: "pending_reviews", label: "Pending reviews", icon: ShieldCheck, href: "/dashboard/reviews" },
  { key: "open_blockers", label: "Open blockers", icon: TriangleAlert, href: "/dashboard/projects" },
  { key: "generated_handovers", label: "Generated handovers", icon: FileText, href: "/dashboard/handovers" },
] as const;

function formatRelativeDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Recently";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(date);
}

function humanize(value: string) {
  return value.replace(/[._]/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function DashboardOverview() {
  const { organization, loading: sessionLoading } = useAppContext();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!organization) {
      setSummary(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await apiRequest<DashboardSummary>(
        `organizations/${organization.id}/dashboard`,
      );
      setSummary(response.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, [organization]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    window.addEventListener("knowbridge:organization-change", load);
    return () => window.removeEventListener("knowbridge:organization-change", load);
  }, [load]);

  const isLoading = sessionLoading || loading;
  return (
    <div className="space-y-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.17em] text-[#a27b35]">
            Workspace overview
          </p>
          <h1 className="mt-2 text-[28px] font-semibold tracking-[-0.045em] text-[#192d45] sm:text-[34px]">
            Good morning{organization ? `, ${organization.name}` : ""}
          </h1>
          <p className="mt-2 text-sm text-[#7b8289]">
            Here’s what’s moving across your knowledge workspace.
          </p>
        </div>
        <Link
          className="inline-flex h-10 items-center justify-center gap-2 self-start rounded-xl bg-[#b88732] px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-[#a57626] sm:self-auto"
          href="/dashboard/projects"
        >
          <GitBranch size={16} />
          View projects
        </Link>
      </div>

      {error && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#e7c9c4] bg-[#fff9f7] px-4 py-3 text-sm text-[#8d3931]" role="alert">
          <span>{error}</span>
          <button className="font-semibold underline" onClick={() => void load()}>Try again</button>
        </div>
      )}

      <section aria-label="Workspace metrics" className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          const value = summary?.[metric.key] ?? 0;
          return (
            <Link
              className="group rounded-2xl border border-[#e9e4db] bg-white p-5 transition hover:-translate-y-0.5 hover:border-[#d9c9a9] hover:shadow-[0_12px_30px_-20px_rgba(27,44,63,0.28)]"
              href={metric.href}
              key={metric.key}
            >
              <div className="flex items-start justify-between">
                <span className="flex size-10 items-center justify-center rounded-xl bg-[#f5f1e8] text-[#a27b35]">
                  <Icon size={18} strokeWidth={1.8} />
                </span>
                <ArrowUpRight className="text-[#b0aca3] transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-[#b88732]" size={17} />
              </div>
              <p className="mt-5 text-[28px] font-semibold tracking-[-0.04em] text-[#192d45]">
                {isLoading ? <span className="inline-block h-8 w-12 animate-pulse rounded bg-[#f0eee9]" /> : value}
              </p>
              <p className="mt-1 text-[13px] text-[#7e858b]">{metric.label}</p>
            </Link>
          );
        })}
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.9fr)]">
        <div className="overflow-hidden rounded-2xl border border-[#e9e4db] bg-white">
          <div className="flex items-center justify-between border-b border-[#efebe4] px-5 py-4 sm:px-6">
            <div>
              <h2 className="text-sm font-semibold text-[#20354d]">Your projects</h2>
              <p className="mt-1 text-xs text-[#8b8f91]">Current work and its knowledge coverage</p>
            </div>
            <Link className="text-xs font-semibold text-[#9b702a] hover:underline" href="/dashboard/projects">
              All projects
            </Link>
          </div>
          {isLoading ? (
            <div className="space-y-3 p-5">
              {[0, 1, 2].map((item) => <div className="h-14 animate-pulse rounded-xl bg-[#f6f4ef]" key={item} />)}
            </div>
          ) : !summary?.projects.length ? (
            <div className="px-6 py-12 text-center">
              <span className="mx-auto flex size-11 items-center justify-center rounded-full bg-[#f5f1e8] text-[#a27b35]"><GitBranch size={19} /></span>
              <h3 className="mt-3 text-sm font-semibold text-[#293d52]">Start with a project</h3>
              <p className="mx-auto mt-1 max-w-xs text-xs leading-5 text-[#858b8e]">Create a workspace for the decisions, documents, and context your team relies on.</p>
              <Link className="mt-4 inline-flex rounded-lg bg-[#182d46] px-3 py-2 text-xs font-semibold text-white hover:bg-[#243f60]" href="/dashboard/projects">Create project</Link>
            </div>
          ) : (
            <div className="divide-y divide-[#f1eee8]">
              {summary.projects.slice(0, 5).map((project) => (
                <div className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:px-6" key={project.id}>
                  <div className="flex min-w-0 flex-1 items-center gap-3">
                    <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-[#f2f3ef] text-[#536c5a]"><GitBranch size={16} /></span>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-[#263b52]">{project.name}</p>
                      <p className="mt-0.5 truncate text-xs text-[#909397]">{project.description || "No description yet"}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-5 pl-12 sm:pl-0">
                    <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold capitalize ${project.status === "active" ? "bg-[#edf4eb] text-[#52714e]" : "bg-[#f3f0e9] text-[#817457]"}`}>{project.status}</span>
                    <span className="flex items-center gap-1 text-xs text-[#858b8e]"><Users size={14} />{project.team_members}</span>
                    <div className="w-24">
                      <div className="flex justify-between text-[10px] text-[#858b8e]"><span>Knowledge</span><span>{project.knowledge_completeness}%</span></div>
                      <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-[#eeece6]"><span className="block h-full rounded-full bg-[#bd9349]" style={{ width: `${project.knowledge_completeness}%` }} /></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-2xl border border-[#e9e4db] bg-white p-5 sm:p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-sm font-semibold text-[#20354d]">Knowledge continuity</h2>
              <p className="mt-1 text-xs text-[#8b8f91]">Projects with captured knowledge</p>
            </div>
            <span className="flex size-9 items-center justify-center rounded-xl bg-[#f5f1e8] text-[#a27b35]"><BookOpen size={17} /></span>
          </div>
          {isLoading ? (
            <div className="mt-8 h-32 animate-pulse rounded-xl bg-[#f6f4ef]" />
          ) : (
            <>
              <div className="mt-7 flex items-center gap-5">
                <div
                  aria-label={`${summary?.continuity_score ?? 0}% knowledge continuity`}
                  className="relative flex size-[112px] shrink-0 items-center justify-center rounded-full"
                  role="img"
                  style={{ background: `conic-gradient(#b88732 ${summary?.continuity_score ?? 0}%, #f0eee8 0)` }}
                >
                  <span className="flex size-[88px] items-center justify-center rounded-full bg-white text-2xl font-semibold tracking-tight text-[#1d3046]">{summary?.continuity_score ?? 0}<span className="ml-0.5 text-sm">%</span></span>
                </div>
                <div>
                  <p className="text-sm font-semibold capitalize text-[#35485b]">{humanize(summary?.continuity_status ?? "needs_attention")}</p>
                  <p className="mt-1 text-xs leading-5 text-[#848a8e]">
                    {summary?.total_projects
                      ? `${summary.projects.filter((project) => project.knowledge_items > 0).length} of ${summary.total_projects} projects have knowledge captured.`
                      : "Create a project to start tracking continuity."}
                  </p>
                </div>
              </div>
              <div className="mt-6 border-t border-[#efebe4] pt-4">
                <p className="text-xs font-semibold text-[#586675]">Recent activity</p>
                {!summary?.recent_activity.length ? (
                  <p className="mt-3 text-xs text-[#909397]">Activity will appear here as your team works.</p>
                ) : (
                  <ul className="mt-3 space-y-3">
                    {summary.recent_activity.slice(0, 4).map((activity) => (
                      <li className="flex gap-2.5" key={activity.id}>
                        <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-[#c09750]" />
                        <div className="min-w-0">
                          <p className="truncate text-[11px] text-[#566575]">
                            <span className="font-semibold">{activity.actor_name ?? "A team member"}</span>{" "}
                            {humanize(activity.action)}
                          </p>
                          <p className="mt-0.5 text-[10px] text-[#9a9da0]">{formatRelativeDate(activity.created_at)}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}

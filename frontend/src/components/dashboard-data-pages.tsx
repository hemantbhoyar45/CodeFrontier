"use client";

import {
  Archive,
  ArrowUpRight,
  BookOpen,
  FileText,
  GitBranch,
  LoaderCircle,
  Plus,
  Search,
  Users,
} from "lucide-react";
import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { useAppContext } from "@/components/app-provider";
import { useToast } from "@/components/toast-provider";
import { apiRequest, getErrorMessage } from "@/lib/api";
import type {
  AuditLog,
  DashboardSummary,
  Document,
  Handover,
  KnowledgeItem,
  OrganizationMember,
  ProjectSummary,
} from "@/lib/types";

type Resource = "projects" | "knowledge" | "documents" | "handovers" | "reviews" | "integrations" | "audit";

const resourceDetails: Record<Resource, { title: string; subtitle: string; icon: typeof BookOpen }> = {
  projects: { title: "Projects", subtitle: "Project spaces and knowledge coverage", icon: GitBranch },
  knowledge: { title: "Knowledge Base", subtitle: "Verified context, findings, and decisions", icon: BookOpen },
  documents: { title: "Documents", subtitle: "Source material across your projects", icon: FileText },
  handovers: { title: "Handover Reports", subtitle: "Reports created to carry context forward", icon: Archive },
  reviews: { title: "Reviews", subtitle: "Human review requests across your workspace", icon: Users },
  integrations: { title: "Integrations", subtitle: "Connected sources for your organization", icon: ArrowUpRight },
  audit: { title: "Audit Logs", subtitle: "Recent activity in your organization", icon: FileText },
};

type GenericItem = Record<string, unknown> & { id: string };

function ResourceError({ message, retry }: { message: string; retry: () => void }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[#e7c9c4] bg-[#fff9f7] px-4 py-3 text-sm text-[#8d3931]" role="alert">
      {message}<button className="font-semibold underline" onClick={retry}>Try again</button>
    </div>
  );
}

function EmptyState({ title, body, href, action }: { title: string; body: string; href?: string; action?: string }) {
  return (
    <div className="px-6 py-14 text-center">
      <span className="mx-auto flex size-11 items-center justify-center rounded-full bg-[#f5f1e8] text-[#a27b35]"><GitBranch size={19} /></span>
      <h3 className="mt-3 text-sm font-semibold text-[#293d52]">{title}</h3>
      <p className="mx-auto mt-1 max-w-xs text-xs leading-5 text-[#858b8e]">{body}</p>
      {href && action && <Link className="mt-4 inline-flex rounded-lg bg-[#182d46] px-3 py-2 text-xs font-semibold text-white hover:bg-[#243f60]" href={href}>{action}</Link>}
    </div>
  );
}

function ProjectForm({ onCreated }: { onCreated: () => void }) {
  const { organization } = useAppContext();
  const { notify } = useToast();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!organization) return;
    setBusy(true);
    setError(null);
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    try {
      await apiRequest(`organizations/${organization.id}/projects`, {
        method: "POST",
        body: JSON.stringify({ name: form.get("name"), description: form.get("description") || null }),
      });
      formElement.reset();
      notify("Project created.");
      onCreated();
    } catch (requestError) {
      setError(getErrorMessage(requestError));
      notify(getErrorMessage(requestError), "error");
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="grid gap-3 rounded-2xl border border-[#e9e4db] bg-white p-4 sm:grid-cols-[1fr_1.4fr_auto] sm:items-end" id="create-project" onSubmit={submit}>
      <label className="text-xs font-semibold text-[#46596a]">Project name<input className="mt-1.5 h-10 w-full rounded-lg border border-[#e3dfd7] px-3 text-sm font-normal outline-none focus:border-[#c89a42]" maxLength={180} minLength={1} name="name" required /></label>
      <label className="text-xs font-semibold text-[#46596a]">Description <span className="font-normal text-[#9a9da0]">(optional)</span><input className="mt-1.5 h-10 w-full rounded-lg border border-[#e3dfd7] px-3 text-sm font-normal outline-none focus:border-[#c89a42]" maxLength={10000} name="description" /></label>
      <button className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-[#182d46] px-4 text-xs font-semibold text-white disabled:opacity-60" disabled={busy} type="submit">{busy ? <LoaderCircle className="animate-spin" size={15} /> : <Plus size={15} />}Create project</button>
      {error && <p className="text-xs text-[#8d3931] sm:col-span-3" role="alert">{error}</p>}
    </form>
  );
}

function ProjectsTable({ projects }: { projects: ProjectSummary[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] text-left">
        <thead className="bg-[#faf9f6] text-[10px] font-semibold uppercase tracking-[0.12em] text-[#92928b]">
          <tr>{["Project", "Owner", "Team", "Status", "Knowledge", "Last updated"].map((item) => <th className="px-5 py-3" key={item}>{item}</th>)}</tr>
        </thead>
        <tbody className="divide-y divide-[#f1eee8]">
          {projects.map((project) => (
            <tr className="hover:bg-[#fdfcf9]" key={project.id}>
              <td className="px-5 py-4"><Link className="text-sm font-semibold text-[#263b52] hover:text-[#9b702a] hover:underline" href={`/dashboard/projects/${project.id}`}>{project.name}</Link><p className="mt-1 max-w-56 truncate text-xs text-[#909397]">{project.description || "No description yet"}</p></td>
              <td className="px-5 py-4 text-xs text-[#65717d]">{project.owner_name ?? "—"}</td>
              <td className="px-5 py-4 text-xs text-[#65717d]">{project.team_members} members</td>
              <td className="px-5 py-4"><span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold capitalize ${project.status === "active" ? "bg-[#edf4eb] text-[#52714e]" : "bg-[#f3f0e9] text-[#817457]"}`}>{project.status}</span></td>
              <td className="px-5 py-4"><div className="w-24"><div className="flex justify-between text-[10px] text-[#858b8e]"><span>{project.knowledge_items} items</span><span>{project.knowledge_completeness}%</span></div><div className="mt-1 h-1.5 overflow-hidden rounded-full bg-[#eeece6]"><span className="block h-full rounded-full bg-[#bd9349]" style={{ width: `${project.knowledge_completeness}%` }} /></div></div></td>
              <td className="px-5 py-4 text-xs text-[#7d858a]">{new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(project.updated_at))}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ProjectsPage() {
  const { organization } = useAppContext();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    if (!organization) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await apiRequest<DashboardSummary>(`organizations/${organization.id}/dashboard`);
      setProjects(data.projects);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, [organization]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    window.addEventListener("knowbridge:organization-change", load);
    return () => window.removeEventListener("knowbridge:organization-change", load);
  }, [load]);
  const filtered = projects.filter((item) => `${item.name} ${item.description ?? ""}`.toLowerCase().includes(search.toLowerCase()));
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-[11px] font-semibold uppercase tracking-[0.17em] text-[#a27b35]">Workspace</p><h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-[#192d45]">Projects</h1><p className="mt-2 text-sm text-[#7b8289]">Keep ownership, team context, and continuity visible.</p></div><div className="text-xs text-[#8a8e90]">{projects.length} {projects.length === 1 ? "project" : "projects"}</div></div>
      <ProjectForm onCreated={() => void load()} />
      {error && <ResourceError message={error} retry={() => void load()} />}
      <section className="overflow-hidden rounded-2xl border border-[#e9e4db] bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#efebe4] px-5 py-4">
          <div><h2 className="text-sm font-semibold text-[#20354d]">All projects</h2><p className="mt-1 text-xs text-[#8b8f91]">Project owner and knowledge coverage are based on current workspace data.</p></div>
          <label className="relative"><Search className="absolute left-3 top-2.5 text-[#9a9b97]" size={15} /><input className="h-9 w-48 rounded-lg border border-[#e8e3da] bg-[#fdfcf9] pl-9 pr-3 text-xs outline-none focus:border-[#c89a42]" onChange={(event) => setSearch(event.target.value)} placeholder="Search projects" value={search} /></label>
        </div>
        {loading ? <div className="space-y-3 p-5">{[0, 1, 2].map((item) => <div className="h-14 animate-pulse rounded-xl bg-[#f6f4ef]" key={item} />)}</div> : filtered.length ? <ProjectsTable projects={filtered} /> : <EmptyState body="Create a project to give decisions, documents, and owners a shared home." href="#create-project" title={search ? "No projects match your search" : "No projects yet"} />}
      </section>
    </div>
  );
}

async function loadProjectResources<T extends GenericItem>(
  organizationId: string,
  projects: ProjectSummary[],
  resource: "knowledge" | "documents" | "handovers",
): Promise<T[]> {
  const responses = await Promise.all(
    projects.map((project) =>
      apiRequest<T[]>(
        `organizations/${organizationId}/projects/${project.id}/${resource}?limit=100`,
      ),
    ),
  );
  return responses.flatMap((response) => response.data);
}

function displayField(value: unknown): string {
  if (typeof value !== "string") return "—";
  return value.replace(/[._]/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function ResourceListPage({ resource }: { resource: Exclude<Resource, "projects"> }) {
  const { organization } = useAppContext();
  const details = resourceDetails[resource];
  const Icon = details.icon;
  const [items, setItems] = useState<GenericItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    if (!organization) return;
    setLoading(true);
    setError(null);
    try {
      if (resource === "reviews" || resource === "integrations" || resource === "audit") {
        const path = {
          reviews: `organizations/${organization.id}/reviews?limit=100`,
          integrations: `organizations/${organization.id}/integrations?limit=100`,
          audit: `organizations/${organization.id}/audit-logs?limit=100`,
        }[resource];
        const response = await apiRequest<GenericItem[]>(path);
        setItems(response.data);
      } else {
        const { data: dashboard } = await apiRequest<DashboardSummary>(`organizations/${organization.id}/dashboard`);
        const records = resource === "documents"
          ? await loadProjectResources<Document & GenericItem>(organization.id, dashboard.projects, "documents")
          : resource === "knowledge"
            ? await loadProjectResources<KnowledgeItem & GenericItem>(organization.id, dashboard.projects, "knowledge")
            : await loadProjectResources<Handover & GenericItem>(organization.id, dashboard.projects, "handovers");
        setItems(records);
      }
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, [organization, resource]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    window.addEventListener("knowbridge:organization-change", load);
    return () => window.removeEventListener("knowbridge:organization-change", load);
  }, [load]);

  const filtered = useMemo(
    () => items.filter((item) => JSON.stringify(item).toLowerCase().includes(search.toLowerCase())),
    [items, search],
  );
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-[11px] font-semibold uppercase tracking-[0.17em] text-[#a27b35]">Workspace</p><h1 className="mt-2 flex items-center gap-3 text-3xl font-semibold tracking-[-0.05em] text-[#192d45]"><Icon className="text-[#b88732]" size={24} />{details.title}</h1><p className="mt-2 text-sm text-[#7b8289]">{details.subtitle}</p></div><span className="text-xs text-[#8a8e90]">{items.length} records</span></div>
      {error && <ResourceError message={error} retry={() => void load()} />}
      <section className="overflow-hidden rounded-2xl border border-[#e9e4db] bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#efebe4] px-5 py-4"><div><h2 className="text-sm font-semibold text-[#20354d]">{details.title}</h2><p className="mt-1 text-xs text-[#8b8f91]">Live records from your selected organization.</p></div><label className="relative"><Search className="absolute left-3 top-2.5 text-[#9a9b97]" size={15} /><input className="h-9 w-48 rounded-lg border border-[#e8e3da] bg-[#fdfcf9] pl-9 pr-3 text-xs outline-none focus:border-[#c89a42]" onChange={(event) => setSearch(event.target.value)} placeholder={`Search ${details.title.toLowerCase()}`} value={search} /></label></div>
        {loading ? <div className="space-y-3 p-5">{[0, 1, 2].map((item) => <div className="h-14 animate-pulse rounded-xl bg-[#f6f4ef]" key={item} />)}</div> : filtered.length ? (
          <div className="divide-y divide-[#f1eee8]">
            {filtered.map((item) => {
              const projectName = "project_id" in item
                ? (item.project_id as string)
                : "";
              const project = "project_id" in item ? projectName.slice(0, 8) : "";
              return (
                <article className="flex flex-wrap items-start justify-between gap-3 px-5 py-4" key={item.id}>
                  <div className="min-w-0 flex-1"><h3 className="truncate text-sm font-semibold text-[#263b52]">{displayField(item.title ?? item.action ?? item.provider ?? item.target_type ?? item.resource_type)}</h3><p className="mt-1 line-clamp-2 text-xs text-[#7d858a]">{displayField(item.description ?? item.content ?? item.comment ?? item.status ?? item.action)}</p>{project && <p className="mt-2 text-[10px] text-[#9a9da0]">Project · {project}</p>}</div>
                  <div className="flex items-center gap-2"><span className="rounded-full bg-[#f3f0e9] px-2.5 py-1 text-[10px] font-semibold capitalize text-[#817457]">{displayField(item.status ?? item.kind ?? item.role ?? item.provider ?? item.resource_type)}</span><span className="text-[10px] text-[#9a9da0]">{typeof item.created_at === "string" ? new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(item.created_at)) : ""}</span></div>
                </article>
              );
            })}
          </div>
        ) : <EmptyState body={`When your team adds ${details.title.toLowerCase()}, they will appear here.`} title={search ? "No results found" : `No ${details.title.toLowerCase()} yet`} />}
      </section>
    </div>
  );
}

export function TeamPage() {
  const { organization, organizationRole, user } = useAppContext();
  const { notify } = useToast();
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [inviteUrl, setInviteUrl] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!organization) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiRequest<OrganizationMember[]>(
        `organizations/${organization.id}/members?limit=100`,
      );
      setMembers(response.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, [organization]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    window.addEventListener("knowbridge:organization-change", load);
    return () => window.removeEventListener("knowbridge:organization-change", load);
  }, [load]);

  async function createInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!organization) return;
    setBusy(true);
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    try {
      const response = await apiRequest<{ token: string }>(
        `organizations/${organization.id}/invitations`,
        { method: "POST", body: JSON.stringify({ email: form.get("email"), role: form.get("role") }) },
      );
      const url = `${window.location.origin}/invite/${encodeURIComponent(response.data.token)}`;
      setInviteUrl(url);
      notify("Invitation link created.");
      formElement.reset();
    } catch (requestError) {
      notify(getErrorMessage(requestError), "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div><p className="text-[11px] font-semibold uppercase tracking-[0.17em] text-[#a27b35]">Workspace</p><h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-[#192d45]">Team members</h1><p className="mt-2 text-sm text-[#7b8289]">Manage organization access and share invitation links.</p></div>
      {(organizationRole === "owner" || organizationRole === "admin") && <form className="grid gap-3 rounded-2xl border border-[#e9e4db] bg-white p-4 sm:grid-cols-[1fr_170px_auto] sm:items-end" onSubmit={createInvite}><label className="text-xs font-semibold text-[#46596a]">Invite by email<input autoComplete="email" className="mt-1.5 h-10 w-full rounded-lg border border-[#e3dfd7] px-3 text-sm font-normal outline-none focus:border-[#c89a42]" name="email" required type="email" /></label><label className="text-xs font-semibold text-[#46596a]">Role<select className="mt-1.5 h-10 w-full rounded-lg border border-[#e3dfd7] bg-white px-3 text-sm font-normal outline-none focus:border-[#c89a42]" name="role"><option value="member">Member</option><option value="admin">Admin</option><option value="viewer">Viewer</option></select></label><button className="h-10 rounded-lg bg-[#182d46] px-4 text-xs font-semibold text-white disabled:opacity-60" disabled={busy} type="submit">{busy ? "Creating…" : "Create invite"}</button>{inviteUrl && <div className="flex flex-wrap items-center gap-2 text-xs sm:col-span-3"><span className="min-w-0 flex-1 truncate rounded-lg bg-[#f6f4ef] px-3 py-2 text-[#65717d]">{inviteUrl}</span><button className="font-semibold text-[#9a6b1b] hover:underline" onClick={() => void navigator.clipboard.writeText(inviteUrl).then(() => notify("Invite link copied."))} type="button">Copy link</button></div>}</form>}
      {error && <ResourceError message={error} retry={() => void load()} />}
      <section className="overflow-hidden rounded-2xl border border-[#e9e4db] bg-white"><div className="border-b border-[#efebe4] px-5 py-4"><h2 className="text-sm font-semibold text-[#20354d]">{organization?.name ?? "Organization"} members</h2><p className="mt-1 text-xs text-[#8b8f91]">{members.length} members</p></div>{loading ? <div className="space-y-3 p-5">{[0, 1, 2].map((item) => <div className="h-12 animate-pulse rounded-xl bg-[#f6f4ef]" key={item} />)}</div> : members.length ? <div className="divide-y divide-[#f1eee8]">{members.map((member) => <div className="flex items-center gap-3 px-5 py-3.5" key={member.id}><span className="flex size-9 items-center justify-center rounded-full bg-[#eee3ce] text-xs font-bold text-[#604a23]">{member.full_name.split(/\s+/).map((part) => part[0]).slice(0, 2).join("").toUpperCase()}</span><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium text-[#2b4056]">{member.full_name}{member.user_id === user?.id ? " (you)" : ""}</p><p className="truncate text-xs text-[#858b8e]">{member.email}</p></div><span className="rounded-full bg-[#f3f0e9] px-2.5 py-1 text-[10px] font-semibold capitalize text-[#817457]">{member.role}</span></div>)}</div> : <EmptyState body="Invite colleagues to share project knowledge and reviews." title="Your team starts here" />}</section>
    </div>
  );
}

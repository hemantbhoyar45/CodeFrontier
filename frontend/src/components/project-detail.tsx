"use client";

import { ArrowLeft, BookOpen, FileText, Users } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { useAppContext } from "@/components/app-provider";
import { apiRequest, getErrorMessage } from "@/lib/api";
import type { DashboardSummary, Document, KnowledgeItem, OrganizationMember, ProjectSummary } from "@/lib/types";

type ProjectDetails = ProjectSummary & { created_at?: string };

export function ProjectDetail() {
  const params = useParams<{ projectId: string }>();
  const { organization } = useAppContext();
  const [project, setProject] = useState<ProjectDetails | null>(null);
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [knowledge, setKnowledge] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!organization || !params.projectId) return;
    setLoading(true);
    setError(null);
    const root = `organizations/${organization.id}`;
    try {
      const [dashboard, memberResponse, documentResponse, knowledgeResponse] = await Promise.all([
        apiRequest<DashboardSummary>(`${root}/dashboard`),
        apiRequest<OrganizationMember[]>(`${root}/projects/${params.projectId}/members?limit=100`),
        apiRequest<Document[]>(`${root}/projects/${params.projectId}/documents?limit=100`),
        apiRequest<KnowledgeItem[]>(`${root}/projects/${params.projectId}/knowledge?limit=100`),
      ]);
      const found = dashboard.data.projects.find((item) => item.id === params.projectId);
      if (!found) throw new Error("Project not found or you do not have access.");
      setProject(found);
      setMembers(memberResponse.data);
      setDocuments(documentResponse.data);
      setKnowledge(knowledgeResponse.data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, [organization, params.projectId]);

  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    window.addEventListener("knowbridge:organization-change", load);
    return () => window.removeEventListener("knowbridge:organization-change", load);
  }, [load]);

  if (loading) return <div className="space-y-4"><div className="h-28 animate-pulse rounded-2xl bg-white" /><div className="grid gap-4 md:grid-cols-3">{[0, 1, 2].map((item) => <div className="h-36 animate-pulse rounded-2xl bg-white" key={item} />)}</div></div>;
  if (error || !project) return <div className="rounded-xl border border-[#e7c9c4] bg-[#fff9f7] p-5 text-sm text-[#8d3931]" role="alert">{error ?? "Project not found."} <button className="ml-3 font-semibold underline" onClick={() => void load()}>Retry</button></div>;

  return (
    <div className="space-y-6">
      <Link className="inline-flex items-center gap-2 text-xs font-semibold text-[#77818a] hover:text-[#233b54]" href="/dashboard/projects"><ArrowLeft size={15} />All projects</Link>
      <section className="rounded-2xl border border-[#e9e4db] bg-white p-6 sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-[11px] font-semibold uppercase tracking-[0.17em] text-[#a27b35]">Project dashboard</p><h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-[#192d45]">{project.name}</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-[#7b8289]">{project.description || "No project description has been added."}</p></div><span className="rounded-full bg-[#edf4eb] px-3 py-1.5 text-xs font-semibold capitalize text-[#52714e]">{project.status}</span></div>
        <div className="mt-7 grid gap-4 border-t border-[#efebe4] pt-5 sm:grid-cols-3"><div><p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#99958d]">Project owner</p><p className="mt-1.5 text-sm font-medium text-[#35485b]">{project.owner_name ?? "—"}</p></div><div><p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#99958d]">Last updated</p><p className="mt-1.5 text-sm font-medium text-[#35485b]">{new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(project.updated_at))}</p></div><div><p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#99958d]">Knowledge completeness</p><div className="mt-2 flex items-center gap-3"><div className="h-2 flex-1 overflow-hidden rounded-full bg-[#eeece6]"><span className="block h-full rounded-full bg-[#bd9349]" style={{ width: `${project.knowledge_completeness}%` }} /></div><span className="text-xs font-semibold text-[#7d7562]">{project.knowledge_completeness}%</span></div></div></div>
      </section>
      <div className="grid gap-4 md:grid-cols-3">
        {[{ label: "Team members", value: members.length, icon: Users }, { label: "Documents", value: documents.length, icon: FileText }, { label: "Knowledge items", value: knowledge.length, icon: BookOpen }].map(({ label, value, icon: Icon }) => <article className="rounded-2xl border border-[#e9e4db] bg-white p-5" key={label}><span className="flex size-9 items-center justify-center rounded-xl bg-[#f5f1e8] text-[#a27b35]"><Icon size={17} /></span><p className="mt-4 text-2xl font-semibold text-[#192d45]">{value}</p><p className="mt-1 text-xs text-[#81888d]">{label}</p></article>)}
      </div>
      <section className="rounded-2xl border border-[#e9e4db] bg-white"><div className="border-b border-[#efebe4] px-5 py-4"><h2 className="text-sm font-semibold text-[#20354d]">Project team</h2></div>{members.length ? <div className="divide-y divide-[#f1eee8]">{members.map((member) => <div className="flex items-center gap-3 px-5 py-3" key={member.id}><span className="flex size-8 items-center justify-center rounded-full bg-[#eee3ce] text-[10px] font-bold text-[#604a23]">{member.full_name.slice(0, 1).toUpperCase()}</span><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium text-[#35485b]">{member.full_name}</p><p className="text-xs text-[#858b8e]">{member.email}</p></div><span className="text-xs capitalize text-[#817457]">{member.role}</span></div>)}</div> : <p className="px-5 py-8 text-center text-xs text-[#8b8f91]">No team members found.</p>}</section>
    </div>
  );
}

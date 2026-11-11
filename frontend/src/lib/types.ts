export type ApiEnvelope<T> = {
  data: T;
  meta?: { count?: number; limit?: number; offset?: number };
};

export type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
};

export type Organization = {
  id: string;
  name: string;
  slug: string;
};

export type OrganizationMember = {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: "owner" | "admin" | "member" | "viewer";
};

export type ProjectSummary = {
  id: string;
  name: string;
  description: string | null;
  status: string;
  created_by: string;
  owner_name: string | null;
  updated_at: string;
  team_members: number;
  knowledge_items: number;
  knowledge_completeness: number;
};

export type DashboardActivity = {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  actor_name: string | null;
  created_at: string;
};

export type DashboardSummary = {
  total_projects: number;
  active_projects: number;
  knowledge_items: number;
  pending_reviews: number;
  open_blockers: number;
  generated_handovers: number;
  continuity_score: number;
  continuity_status: "strong" | "building" | "needs_attention";
  projects: ProjectSummary[];
  recent_activity: DashboardActivity[];
};

export type Document = {
  id: string;
  project_id: string;
  title: string;
  source_uri: string | null;
  content_type: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type KnowledgeItem = {
  id: string;
  project_id: string;
  title: string;
  content: string;
  kind: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type Handover = {
  id: string;
  project_id: string;
  title: string;
  recipient_role: string | null;
  content: Record<string, unknown>;
  status: string;
  created_at: string;
  updated_at: string;
};

export type AuditLog = {
  id: string;
  actor_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: Record<string, unknown>;
  created_at: string;
};

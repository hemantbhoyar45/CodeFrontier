"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest } from "@/lib/api";
import type { Organization, User } from "@/lib/types";

type AppContextValue = {
  user: User | null;
  organizations: Organization[];
  organization: Organization | null;
  organizationRole: string | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  selectOrganization: (id: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AppContext = createContext<AppContextValue | null>(null);
const activeOrganizationKey = "knowbridge.active-organization";

export function AppProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [activeOrganizationId, setActiveOrganizationId] = useState<string | null>(null);
  const [organizationRole, setOrganizationRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [profile, orgs] = await Promise.all([
        apiRequest<User>("auth/me"),
        apiRequest<Organization[]>("organizations"),
      ]);
      setUser(profile.data);
      setOrganizations(orgs.data);
      const storedId = window.localStorage.getItem(activeOrganizationKey);
      const nextOrganization =
        orgs.data.find((item) => item.id === storedId) ?? orgs.data[0] ?? null;
      setActiveOrganizationId(nextOrganization?.id ?? null);
      if (nextOrganization) {
        window.localStorage.setItem(activeOrganizationKey, nextOrganization.id);
        const membership = await apiRequest<{ role: string }>(
          `organizations/${nextOrganization.id}/members/me`,
        );
        setOrganizationRole(membership.data.role);
      } else {
        window.localStorage.removeItem(activeOrganizationKey);
        setOrganizationRole(null);
      }
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Unable to load your workspace.",
      );
      if ("status" in (requestError as object) && (requestError as { status?: number }).status === 401) {
        router.replace("/login");
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const selectOrganization = useCallback(async (id: string) => {
    setActiveOrganizationId(id);
    window.localStorage.setItem(activeOrganizationKey, id);
    window.dispatchEvent(new CustomEvent("knowbridge:organization-change", { detail: id }));
    if (user) {
      try {
        const membership = await apiRequest<{ role: string }>(
          `organizations/${id}/members/me`,
        );
        setOrganizationRole(membership.data.role);
      } catch {
        setOrganizationRole(null);
      }
    }
  }, [user]);

  const signOut = useCallback(async () => {
    await fetch("/api/backend/auth/logout", { method: "POST" });
    setUser(null);
    router.replace("/login");
    router.refresh();
  }, [router]);

  const organization =
    organizations.find((item) => item.id === activeOrganizationId) ?? null;
  const value = useMemo(
    () => ({
      user,
      organizations,
      organization,
      organizationRole,
      loading,
      error,
      refresh,
      selectOrganization,
      signOut,
    }),
    [
      user,
      organizations,
      organization,
      organizationRole,
      loading,
      error,
      refresh,
      selectOrganization,
      signOut,
    ],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const value = useContext(AppContext);
  if (!value) throw new Error("useAppContext must be used within AppProvider.");
  return value;
}

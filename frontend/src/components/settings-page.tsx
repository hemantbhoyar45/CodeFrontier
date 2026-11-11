"use client";

import { FormEvent, useState } from "react";

import { useAppContext } from "@/components/app-provider";
import { useToast } from "@/components/toast-provider";
import { apiRequest, getErrorMessage } from "@/lib/api";

export function SettingsPage() {
  const { user, organization, refresh, selectOrganization } = useAppContext();
  const { notify } = useToast();
  const [profileBusy, setProfileBusy] = useState(false);
  const [organizationBusy, setOrganizationBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function updateProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setProfileBusy(true);
    setError(null);
    try {
      await apiRequest("auth/me", {
        method: "PATCH",
        body: JSON.stringify({
          full_name: form.get("full_name"),
          email: form.get("email"),
        }),
      });
      await refresh();
      notify("Profile updated.");
    } catch (requestError) {
      setError(getErrorMessage(requestError));
      notify(getErrorMessage(requestError), "error");
    } finally {
      setProfileBusy(false);
    }
  }

  async function createOrganization(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    setOrganizationBusy(true);
    setError(null);
    try {
      const response = await apiRequest<{ id: string }>("organizations", {
        method: "POST",
        body: JSON.stringify({ name: form.get("name") }),
      });
      await refresh();
      await selectOrganization(response.data.id);
      formElement.reset();
      notify("Organization created.");
    } catch (requestError) {
      setError(getErrorMessage(requestError));
      notify(getErrorMessage(requestError), "error");
    } finally {
      setOrganizationBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-[0.17em] text-[#a27b35]">Workspace</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-[#192d45]">Settings</h1>
        <p className="mt-2 text-sm text-[#7b8289]">Manage your profile and organization workspaces.</p>
      </div>
      {error && <div className="rounded-xl border border-[#e7c9c4] bg-[#fff9f7] px-4 py-3 text-sm text-[#8d3931]" role="alert">{error}</div>}
      <section className="rounded-2xl border border-[#e9e4db] bg-white p-5 sm:p-6">
        <h2 className="text-sm font-semibold text-[#20354d]">Your profile</h2>
        <p className="mt-1 text-xs text-[#8b8f91]">These details are associated with your account.</p>
        <form className="mt-5 grid gap-4 sm:max-w-xl" onSubmit={updateProfile}>
          <label className="text-xs font-semibold text-[#46596a]">Full name<input autoComplete="name" className="mt-1.5 h-10 w-full rounded-lg border border-[#e3dfd7] px-3 text-sm font-normal outline-none focus:border-[#c89a42]" defaultValue={user?.full_name ?? ""} key={user?.full_name} maxLength={160} minLength={1} name="full_name" required /></label>
          <label className="text-xs font-semibold text-[#46596a]">Email address<input autoComplete="email" className="mt-1.5 h-10 w-full rounded-lg border border-[#e3dfd7] px-3 text-sm font-normal outline-none focus:border-[#c89a42]" defaultValue={user?.email ?? ""} key={user?.email} maxLength={320} name="email" required type="email" /></label>
          <button className="h-10 w-fit rounded-lg bg-[#182d46] px-4 text-xs font-semibold text-white disabled:opacity-60" disabled={profileBusy} type="submit">{profileBusy ? "Saving…" : "Save profile"}</button>
        </form>
      </section>
      <section className="rounded-2xl border border-[#e9e4db] bg-white p-5 sm:p-6">
        <h2 className="text-sm font-semibold text-[#20354d]">Current organization</h2>
        <p className="mt-1 text-xs text-[#8b8f91]">Switch organizations from the sidebar. You are currently working in <strong className="font-semibold text-[#46596a]">{organization?.name ?? "no organization"}</strong>.</p>
        <h3 className="mt-6 text-sm font-semibold text-[#20354d]">Create an organization</h3>
        <p className="mt-1 text-xs text-[#8b8f91]">Create a separate workspace for another team or business unit.</p>
        <form className="mt-4 flex max-w-xl flex-wrap gap-3" onSubmit={createOrganization}>
          <input aria-label="Organization name" className="h-10 min-w-0 flex-1 rounded-lg border border-[#e3dfd7] px-3 text-sm outline-none focus:border-[#c89a42]" maxLength={160} minLength={1} name="name" placeholder="Organization name" required />
          <button className="h-10 rounded-lg border border-[#d9c9a7] px-4 text-xs font-semibold text-[#76551f] hover:bg-[#fbf8f0] disabled:opacity-60" disabled={organizationBusy} type="submit">{organizationBusy ? "Creating…" : "Create organization"}</button>
        </form>
      </section>
    </div>
  );
}

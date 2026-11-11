"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { apiRequest, getErrorMessage } from "@/lib/api";

type Invitation = {
  organization_id: string;
  organization_name: string;
  invited_email: string;
  role: string;
  expires_at: string;
};

export function InvitationPage() {
  const params = useParams<{ token: string }>();
  const token = params.token;
  const [invitation, setInvitation] = useState<Invitation | null>(null);
  const [signedIn, setSignedIn] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const response = await apiRequest<Invitation>(
          `organizations/invitations/${encodeURIComponent(token)}`,
        );
        if (active) setInvitation(response.data);
      } catch (requestError) {
        if (active) setError(getErrorMessage(requestError));
      }
      try {
        await apiRequest("auth/me");
        if (active) setSignedIn(true);
      } catch {
        if (active) setSignedIn(false);
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => { active = false; };
  }, [token]);

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-12">
      <section className="w-full max-w-lg rounded-2xl border border-[#e9e4db] bg-white p-7 shadow-[0_24px_70px_-45px_rgba(27,44,63,0.3)] sm:p-9">
        <p className="text-[10px] font-semibold uppercase tracking-[0.17em] text-[#a27b35]">Organization invitation</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-[#192d45]">Join your team</h1>
        {loading ? <div className="mt-6 h-24 animate-pulse rounded-xl bg-[#f6f4ef]" /> : error || !invitation ? (
          <div className="mt-6 rounded-xl border border-[#e7c9c4] bg-[#fff9f7] p-4 text-sm text-[#8d3931]" role="alert">{error ?? "This invitation is no longer available."}</div>
        ) : (
          <>
            <p className="mt-3 text-sm leading-6 text-[#747e86]">You’ve been invited to join <strong className="font-semibold text-[#35485b]">{invitation.organization_name}</strong> as a <strong className="font-semibold capitalize text-[#35485b]">{invitation.role}</strong>.</p>
            <p className="mt-2 text-xs text-[#8c9295]">Invitation for {invitation.invited_email} · Expires {new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(invitation.expires_at))}</p>
            {signedIn ? (
              <AcceptInvitation token={token} />
            ) : (
              <div className="mt-7 grid gap-3">
                <Link className="inline-flex h-11 items-center justify-center rounded-xl bg-[#182d46] text-sm font-semibold text-white hover:bg-[#263f5c]" href={`/login?next=${encodeURIComponent(`/invite/${token}`)}`}>Sign in to accept</Link>
                <Link className="inline-flex h-11 items-center justify-center rounded-xl border border-[#e3dfd7] bg-white text-sm font-semibold text-[#35485b] hover:bg-[#faf9f6]" href={`/signup?invite=${encodeURIComponent(token)}`}>Create an account</Link>
              </div>
            )}
          </>
        )}
      </section>
    </main>
  );
}

function AcceptInvitation({ token }: { token: string }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [accepted, setAccepted] = useState(false);

  async function accept() {
    setBusy(true);
    setError(null);
    try {
      const response = await apiRequest<{ organization_id: string }>(
        `organizations/invitations/${encodeURIComponent(token)}/accept`,
        { method: "POST" },
      );
      window.localStorage.setItem("knowbridge.active-organization", response.data.organization_id);
      setAccepted(true);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  }

  if (accepted) {
    return <div className="mt-7"><p className="text-sm font-medium text-[#52714e]" role="status">You’ve joined the organization.</p><Link className="mt-4 inline-flex h-11 w-full items-center justify-center rounded-xl bg-[#182d46] text-sm font-semibold text-white hover:bg-[#263f5c]" href="/dashboard">Open workspace</Link></div>;
  }
  return <div className="mt-7"><button className="h-11 w-full rounded-xl bg-[#182d46] text-sm font-semibold text-white hover:bg-[#263f5c] disabled:opacity-60" disabled={busy} onClick={() => void accept()} type="button">{busy ? "Accepting…" : "Accept invitation"}</button>{error && <p className="mt-3 text-xs text-[#8d3931]" role="alert">{error}</p>}</div>;
}

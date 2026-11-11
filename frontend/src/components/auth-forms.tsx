"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { apiRequest, getErrorMessage } from "@/lib/api";

function Field({
  label,
  name,
  type = "text",
  autoComplete,
  required = true,
  minLength,
  defaultValue,
}: {
  label: string;
  name: string;
  type?: string;
  autoComplete?: string;
  required?: boolean;
  minLength?: number;
  defaultValue?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-semibold text-[#46596a]">{label}</span>
      <input
        autoComplete={autoComplete}
        className="h-11 w-full rounded-xl border border-[#e3dfd7] bg-white px-3.5 text-sm text-[#20354d] outline-none transition placeholder:text-[#b2b0aa] focus:border-[#c89a42] focus:ring-2 focus:ring-[#c89a42]/20"
        defaultValue={defaultValue}
        minLength={minLength}
        name={name}
        required={required}
        type={type}
      />
    </label>
  );
}

function SubmitButton({ label, busy }: { label: string; busy: boolean }) {
  return (
    <button
      className="mt-2 inline-flex h-11 w-full items-center justify-center rounded-xl bg-[#182d46] px-4 text-sm font-semibold text-white transition hover:bg-[#263f5c] disabled:cursor-not-allowed disabled:opacity-60"
      disabled={busy}
      type="submit"
    >
      {busy ? "Please wait…" : label}
    </button>
  );
}

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const form = new FormData(event.currentTarget);
    try {
      await apiRequest("auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password"),
        }),
      });
      const next = searchParams.get("next");
      const invitationMatch = next?.match(/^\/invite\/([^/?#]+)/);
      if (invitationMatch) {
        const invitation = await apiRequest<{ organization_id: string }>(
          `organizations/invitations/${encodeURIComponent(invitationMatch[1])}/accept`,
          { method: "POST" },
        );
        window.localStorage.setItem(
          "knowbridge.active-organization",
          invitation.data.organization_id,
        );
      }
      router.replace(next?.startsWith("/dashboard") ? next : "/dashboard");
      router.refresh();
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={submit}>
      <Field autoComplete="email" label="Work email" name="email" type="email" />
      <Field autoComplete="current-password" label="Password" name="password" type="password" />
      {error && <p className="rounded-lg border border-[#e7c9c4] bg-[#fff9f7] px-3 py-2 text-xs text-[#8d3931]" role="alert">{error}</p>}
      <div className="-mt-1 flex justify-end">
        <Link className="text-xs font-semibold text-[#9a6b1b] hover:underline" href="/forgot-password">Forgot password?</Link>
      </div>
      <SubmitButton busy={busy} label="Sign in" />
      <p className="pt-1 text-center text-xs text-[#858a8d]">
        New to KNOWBRIDGE? <Link className="font-semibold text-[#9a6b1b] hover:underline" href="/signup">Create an account</Link>
      </p>
    </form>
  );
}

export function SignupForm({ invitationToken }: { invitationToken?: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    try {
      const response = await apiRequest<{
        user: { id: string };
        organization: { id: string };
      }>("auth/register", {
        method: "POST",
        body: JSON.stringify({
          full_name: form.get("full_name"),
          email: form.get("email"),
          password: form.get("password"),
          organization_name: form.get("organization_name"),
        }),
      });
      const joinedOrganization = invitationToken
        ? await apiRequest<{ organization_id: string }>(
            `organizations/invitations/${encodeURIComponent(invitationToken)}/accept`,
            { method: "POST" },
          )
        : null;
      window.localStorage.setItem(
        "knowbridge.active-organization",
        joinedOrganization?.data.organization_id ?? response.data.organization.id,
      );
      router.replace("/dashboard");
      router.refresh();
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={submit}>
      <Field autoComplete="name" label="Full name" name="full_name" />
      <Field autoComplete="email" label="Work email" name="email" type="email" />
      <Field autoComplete="new-password" label="Password" minLength={12} name="password" type="password" />
      <Field autoComplete="organization" label="Organization" name="organization_name" />
      <p className="-mt-2 text-[11px] leading-5 text-[#8a8d8e]">Use at least 12 characters. You can create or join additional workspaces later.</p>
      {error && <p className="rounded-lg border border-[#e7c9c4] bg-[#fff9f7] px-3 py-2 text-xs text-[#8d3931]" role="alert">{error}</p>}
      <SubmitButton busy={busy} label="Create account" />
      <p className="pt-1 text-center text-xs text-[#858a8d]">
        Already have an account? <Link className="font-semibold text-[#9a6b1b] hover:underline" href="/login">Sign in</Link>
      </p>
    </form>
  );
}

export function ForgotPasswordForm() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const email = new FormData(event.currentTarget).get("email");
    try {
      await apiRequest("auth/password-reset/request", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setSent(true);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <div className="rounded-xl border border-[#d7e5d4] bg-[#f4f8f2] p-4 text-sm leading-6 text-[#4c694a]" role="status">
        If an account exists for that address, password reset instructions are on their way.
      </div>
    );
  }
  return (
    <form className="space-y-4" onSubmit={submit}>
      <Field autoComplete="email" label="Work email" name="email" type="email" />
      {error && <p className="rounded-lg border border-[#e7c9c4] bg-[#fff9f7] px-3 py-2 text-xs text-[#8d3931]" role="alert">{error}</p>}
      <SubmitButton busy={busy} label="Send reset instructions" />
      <p className="pt-1 text-center text-xs"><Link className="font-semibold text-[#9a6b1b] hover:underline" href="/login">Back to sign in</Link></p>
    </form>
  );
}

export function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const form = new FormData(event.currentTarget);
    const token = searchParams.get("token");
    if (!token) {
      setError("This reset link is incomplete. Request a new one to continue.");
      setBusy(false);
      return;
    }
    try {
      await apiRequest("auth/password-reset/confirm", {
        method: "POST",
        body: JSON.stringify({ token, password: form.get("password") }),
      });
      router.replace("/login?reset=success");
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={submit}>
      <Field autoComplete="new-password" label="New password" minLength={12} name="password" type="password" />
      <p className="-mt-2 text-[11px] leading-5 text-[#8a8d8e]">Use at least 12 characters.</p>
      {error && <p className="rounded-lg border border-[#e7c9c4] bg-[#fff9f7] px-3 py-2 text-xs text-[#8d3931]" role="alert">{error}</p>}
      <SubmitButton busy={busy} label="Update password" />
      <p className="pt-1 text-center text-xs"><Link className="font-semibold text-[#9a6b1b] hover:underline" href="/login">Back to sign in</Link></p>
    </form>
  );
}

"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

import { AuthPanel } from "@/components/auth-panel";
import { SignupForm } from "@/components/auth-forms";

function SignupContent() {
  const searchParams = useSearchParams();
  const invitationToken = searchParams.get("invite") ?? undefined;
  return (
    <AuthPanel
      description="Create your account and start building continuity from day one."
      eyebrow="Get started"
      footer={<>Your workspace is private to your organization.</>}
      title="Create your account"
    >
      <SignupForm invitationToken={invitationToken} />
    </AuthPanel>
  );
}

export default function SignupPage() {
  return <Suspense fallback={<div className="min-h-screen animate-pulse bg-[#f7f5f0]" />}><SignupContent /></Suspense>;
}

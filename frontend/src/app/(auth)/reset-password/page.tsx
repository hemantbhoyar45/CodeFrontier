"use client";

import { Suspense } from "react";

import { AuthPanel } from "@/components/auth-panel";
import { ResetPasswordForm } from "@/components/auth-forms";

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-screen animate-pulse bg-[#f7f5f0]" />}>
      <AuthPanel
        description="Choose a new password for your KNOWBRIDGE account."
        eyebrow="Account recovery"
        footer={<>Your account security matters.</>}
        title="Reset password"
      >
        <ResetPasswordForm />
      </AuthPanel>
    </Suspense>
  );
}

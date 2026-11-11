import { Suspense } from "react";

import { AuthPanel } from "@/components/auth-panel";
import { LoginForm } from "@/components/auth-forms";

export default function LoginPage() {
  return (
    <AuthPanel
      description="Sign in to pick up where your team left off."
      eyebrow="Welcome back"
      footer={<>By continuing, you agree to keep shared workspace information secure.</>}
      title="Sign in to your workspace"
    >
      <Suspense fallback={<div className="h-44 animate-pulse rounded-xl bg-[#f0eee9]" />}>
        <LoginForm />
      </Suspense>
    </AuthPanel>
  );
}

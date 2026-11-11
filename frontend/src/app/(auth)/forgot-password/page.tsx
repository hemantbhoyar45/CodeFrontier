import Link from "next/link";

import { AuthPanel } from "@/components/auth-panel";
import { ForgotPasswordForm } from "@/components/auth-forms";

export default function ForgotPasswordPage() {
  return (
    <AuthPanel
      description="Enter the email address linked to your account."
      eyebrow="Account recovery"
      footer={<>Remembered your password? <Link className="font-semibold text-[#9a6b1b] hover:underline" href="/login">Sign in</Link></>}
      title="Reset your password"
    >
      <ForgotPasswordForm />
    </AuthPanel>
  );
}

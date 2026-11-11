import Link from "next/link";

import { BrandMark } from "@/components/brand-mark";

export function AuthPanel({
  eyebrow,
  title,
  description,
  children,
  footer,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[minmax(0,1.05fr)_minmax(420px,0.95fr)]">
      <section className="relative hidden overflow-hidden bg-[#172b43] px-12 py-12 text-white lg:flex lg:flex-col lg:justify-between xl:px-20">
        <div aria-hidden="true" className="absolute -right-36 -top-32 size-[520px] rounded-full border border-white/10" />
        <div aria-hidden="true" className="absolute -right-12 -top-8 size-[360px] rounded-full border border-white/10" />
        <Link className="relative z-10 inline-flex w-fit items-center gap-3" href="/">
          <BrandMark />
          <span className="text-[13px] font-bold tracking-[0.17em]">KNOWBRIDGE</span>
        </Link>
        <div className="relative z-10 max-w-xl pb-12">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#d3aa5b]">Continuity for teams</p>
          <h1 className="mt-5 text-5xl font-medium leading-[1.05] tracking-[-0.06em] xl:text-6xl">
            Keep the knowledge behind the work.
          </h1>
          <p className="mt-6 max-w-md text-sm leading-7 text-white/65">
            Decisions, evidence, and project context—kept clear for the people moving things forward.
          </p>
          <div className="mt-9 flex items-center gap-2 text-xs text-white/55">
            <span className="size-1.5 rounded-full bg-[#d3aa5b]" />
            Evidence-led by design. People-approved by default.
          </div>
        </div>
        <p className="relative z-10 text-[11px] text-white/40">KNOWBRIDGE · Knowledge that moves with your team.</p>
      </section>
      <section className="flex items-center justify-center px-5 py-10 sm:px-10">
        <div className="w-full max-w-[420px]">
          <Link className="mb-9 inline-flex items-center gap-2 lg:hidden" href="/">
            <BrandMark />
            <span className="text-[12px] font-bold tracking-[0.15em] text-[#172b43]">KNOWBRIDGE</span>
          </Link>
          <p className="text-[10px] font-semibold uppercase tracking-[0.17em] text-[#a27b35]">{eyebrow}</p>
          <h2 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-[#192d45]">{title}</h2>
          <p className="mt-2 text-sm leading-6 text-[#7b8289]">{description}</p>
          <div className="mt-8">{children}</div>
          <div className="mt-7 border-t border-[#e7e2d9] pt-5 text-center text-xs text-[#858a8d]">{footer}</div>
        </div>
      </section>
    </div>
  );
}

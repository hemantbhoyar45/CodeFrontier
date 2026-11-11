import {
  ArrowDown,
  ArrowUpRight,
  BookOpenCheck,
  CircleCheck,
  GitBranch,
  Layers3,
  Network,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";

import { BrandMark } from "@/components/brand-mark";
import { Button } from "@/components/ui/button";

const workflow = [
  {
    number: "01",
    title: "Connect",
    description: "Bring authorized knowledge sources into one workspace.",
    icon: Layers3,
  },
  {
    number: "02",
    title: "Reconstruct",
    description: "Turn scattered context into a living project picture.",
    icon: Network,
  },
  {
    number: "03",
    title: "Verify",
    description: "Tie every important claim back to its original evidence.",
    icon: ShieldCheck,
  },
  {
    number: "04",
    title: "Review",
    description: "Keep people in control of what becomes trusted knowledge.",
    icon: CircleCheck,
  },
  {
    number: "05",
    title: "Handover",
    description: "Make the context someone needs clear and actionable.",
    icon: BookOpenCheck,
  },
];

export default function Home() {
  return (
    <div className="relative min-h-screen">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-52 -top-56 size-[36rem] rounded-full border border-[#dce7df] sm:-right-40 sm:-top-64"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-28 -top-32 size-[27rem] rounded-full border border-[#e4ece6]"
      />

      <header className="relative z-10 mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 sm:px-10 lg:px-14">
        <Link aria-label="KNOWBRIDGE home" className="group flex items-center gap-3" href="/">
          <span className="transition-transform group-hover:-rotate-3">
            <BrandMark />
          </span>
          <span className="text-sm font-bold tracking-[0.18em] text-[#183b32]">
            KNOWBRIDGE
          </span>
        </Link>
        <a
          className="inline-flex items-center gap-2 rounded-full border border-[#d9e3dc] bg-white/80 px-4 py-2 text-sm font-medium text-[#31564a] shadow-sm transition-colors hover:border-[#9bb9a7] hover:bg-white"
          href="http://localhost:8000/docs"
          rel="noreferrer"
          target="_blank"
        >
          API reference
          <ArrowUpRight aria-hidden="true" size={15} />
        </a>
      </header>

      <section className="relative z-10 mx-auto grid w-full max-w-7xl gap-14 px-6 pb-20 pt-12 sm:px-10 sm:pt-20 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-16 lg:px-14 lg:pb-28 lg:pt-24">
        <div className="max-w-2xl">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-[#dce8df] bg-white/70 px-3 py-1.5 text-xs font-semibold tracking-wide text-[#38634f]">
            <span className="size-1.5 rounded-full bg-[#668d6f]" />
            KNOWLEDGE CONTINUITY, BUILT FOR TEAMS
          </div>
          <h1 className="max-w-xl text-[clamp(3.35rem,8vw,6.6rem)] font-medium leading-[0.96] tracking-[-0.075em] text-[#16372f]">
            Good work
            <br />
            should outlast
            <br />
            <span className="font-serif font-normal italic text-[#718a70]">
              a handoff.
            </span>
          </h1>
          <p className="mt-8 max-w-lg text-base leading-7 text-[#61716b] sm:text-lg sm:leading-8">
            KNOWBRIDGE helps teams preserve the decisions, dependencies, and
            hard-won context behind their work—grounded in evidence, carried
            forward by people.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <Button
              className="h-11 rounded-full bg-[#173d33] px-5 text-sm text-white hover:bg-[#245344]"
              render={<a href="#approach" />}
            >
              Explore the approach
              <ArrowDown aria-hidden="true" size={16} />
            </Button>
            <span className="text-sm text-[#7b8982]">
              A clearer picture, from day one.
            </span>
          </div>
          <div className="mt-12 flex items-center gap-3 border-t border-[#dce5de] pt-5 text-xs font-medium text-[#74847b]">
            <ShieldCheck aria-hidden="true" className="text-[#66866d]" size={17} />
            Evidence-led by design. People-approved by default.
          </div>
        </div>

        <div
          aria-label="KNOWBRIDGE turns project knowledge into an evidence-backed handover"
          className="relative mx-auto w-full max-w-[34rem]"
          role="img"
        >
          <div className="absolute -inset-4 rounded-[2rem] bg-[#e8eee6]/60 blur-2xl" />
          <div className="relative overflow-hidden rounded-[1.65rem] border border-[#dce5dd] bg-[#fbfcf9] p-5 shadow-[0_24px_80px_-36px_rgba(27,62,47,0.28)] sm:p-7">
            <div className="flex items-center justify-between border-b border-[#e7ece7] pb-5">
              <div>
                <p className="text-[11px] font-semibold tracking-[0.14em] text-[#819087]">
                  THE KNOWLEDGE BRIDGE
                </p>
                <p className="mt-1 text-sm font-medium text-[#29443a]">
                  From context to continuity
                </p>
              </div>
              <span className="flex size-9 items-center justify-center rounded-xl bg-[#edf3ec] text-[#54735b]">
                <Network aria-hidden="true" size={17} />
              </span>
            </div>

            <div className="relative py-7">
              <div
                aria-hidden="true"
                className="absolute bottom-12 left-[1.45rem] top-12 w-px bg-gradient-to-b from-[#b9cbb9] via-[#8fab91] to-[#d8e2d6]"
              />
              <div className="space-y-5">
                <div className="relative flex items-center gap-4">
                  <span className="relative z-10 flex size-12 shrink-0 items-center justify-center rounded-2xl border border-[#dde8de] bg-white text-[#57785d] shadow-sm">
                    <Layers3 aria-hidden="true" size={19} />
                  </span>
                  <div className="min-w-0 flex-1 rounded-xl border border-[#e5ebe4] bg-white px-4 py-3">
                    <p className="text-xs font-semibold text-[#345143]">Team knowledge</p>
                    <p className="mt-1 text-xs text-[#8a968e]">
                      Decisions · docs · project history
                    </p>
                  </div>
                </div>
                <div className="relative flex items-center gap-4">
                  <span className="relative z-10 flex size-12 shrink-0 items-center justify-center rounded-2xl bg-[#193f34] text-[#e9f0e7] shadow-sm">
                    <GitBranch aria-hidden="true" size={19} />
                  </span>
                  <div className="min-w-0 flex-1 rounded-xl border border-[#d9e5d9] bg-[#f2f6f0] px-4 py-3">
                    <p className="text-xs font-semibold text-[#29483b]">
                      KNOWBRIDGE
                    </p>
                    <p className="mt-1 text-xs text-[#75877a]">
                      Reconstructed · evidence-linked · reviewed
                    </p>
                  </div>
                </div>
                <div className="relative flex items-center gap-4">
                  <span className="relative z-10 flex size-12 shrink-0 items-center justify-center rounded-2xl border border-[#e7e8d9] bg-[#faf9ef] text-[#8b8757] shadow-sm">
                    <BookOpenCheck aria-hidden="true" size={19} />
                  </span>
                  <div className="min-w-0 flex-1 rounded-xl border border-[#ecebdd] bg-white px-4 py-3">
                    <p className="text-xs font-semibold text-[#5b5b43]">A confident handover</p>
                    <p className="mt-1 text-xs text-[#929082]">
                      Context that moves work forward
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between border-t border-[#e7ece7] pt-4 text-[11px] font-medium text-[#819087]">
              <span>Source-backed, never guesswork</span>
              <span className="flex items-center gap-1.5 text-[#6b886e]">
                <span className="size-1.5 rounded-full bg-[#82a180]" />
                Human reviewed
              </span>
            </div>
          </div>
          <div className="absolute -bottom-5 -left-3 hidden rounded-xl border border-[#e3e8dc] bg-white px-4 py-3 shadow-[0_12px_35px_-20px_rgba(29,58,43,0.3)] sm:block lg:-left-7">
            <p className="text-[10px] font-semibold tracking-[0.1em] text-[#87948a]">
              THE PRINCIPLE
            </p>
            <p className="mt-1 text-xs font-medium text-[#405c4c]">
              Preserve what matters.
            </p>
          </div>
        </div>
      </section>

      <section
        className="relative z-10 border-y border-[#e2e8e1] bg-[#f0f3ed]/75"
        id="approach"
      >
        <div className="mx-auto max-w-7xl px-6 py-16 sm:px-10 sm:py-20 lg:px-14">
          <div className="mb-10 flex flex-col justify-between gap-4 sm:mb-12 sm:flex-row sm:items-end">
            <div>
              <p className="text-xs font-semibold tracking-[0.16em] text-[#758d79]">
                A THOUGHTFUL FLOW
              </p>
              <h2 className="mt-3 text-3xl font-medium tracking-[-0.045em] text-[#203c31] sm:text-4xl">
                Knowledge, carried forward.
              </h2>
            </div>
            <p className="max-w-sm text-sm leading-6 text-[#748078]">
              Each step adds clarity without losing the source, the nuance, or
              the human judgment behind it.
            </p>
          </div>

          <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {workflow.map(({ number, title, description, icon: Icon }) => (
              <li
                className="group rounded-2xl border border-[#e0e7df] bg-white/80 p-5 transition-all hover:-translate-y-1 hover:border-[#c5d5c6] hover:bg-white hover:shadow-[0_16px_34px_-24px_rgba(24,62,44,0.28)]"
                key={number}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold tracking-[0.12em] text-[#9aa69c]">
                    {number}
                  </span>
                  <Icon
                    aria-hidden="true"
                    className="text-[#69846c] transition-transform group-hover:scale-110"
                    size={18}
                    strokeWidth={1.8}
                  />
                </div>
                <h3 className="mt-6 text-[15px] font-semibold text-[#2e493a]">
                  {title}
                </h3>
                <p className="mt-2 text-xs leading-5 text-[#7b8980]">
                  {description}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <footer className="relative z-10 mx-auto flex w-full max-w-7xl flex-col gap-3 px-6 py-7 text-xs text-[#87948c] sm:flex-row sm:items-center sm:justify-between sm:px-10 lg:px-14">
        <p>KNOWBRIDGE — knowledge that moves with your team.</p>
        <p>Built on evidence. Designed for continuity.</p>
      </footer>
    </div>
  );
}

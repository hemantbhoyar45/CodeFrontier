import { GitBranch } from "lucide-react";

export function BrandMark() {
  return (
    <span
      aria-hidden="true"
      className="flex size-10 items-center justify-center rounded-xl bg-[#173d33] text-[#e9f1e8] shadow-sm"
    >
      <GitBranch size={18} strokeWidth={1.8} />
    </span>
  );
}

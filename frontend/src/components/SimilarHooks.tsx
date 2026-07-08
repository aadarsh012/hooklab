import type { SimilarHook } from "@/types/analysis";

interface Props {
  hooks: SimilarHook[];
}

function formatEngagement(ratio: number): string {
  if (ratio <= 0) return "";
  const pct = ratio * 100;
  return pct >= 1 ? `${pct.toFixed(1)}%` : `${(pct * 10).toFixed(1)}‰`;
}

export default function SimilarHooks({ hooks }: Props) {
  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-5">
      <h3 className="font-semibold text-white mb-1">Real hooks yours resembles</h3>
      <p className="text-sm text-gray-500 mb-4">
        Proof the shape works — these landed big.
      </p>

      <div className="divide-y divide-[#2a2a2a]">
        {hooks.map((hook, i) => (
          <div key={i} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
            <div className="min-w-0 pr-3">
              <p className="text-sm text-white truncate">&ldquo;{hook.hook_text}&rdquo;</p>
              <p className="text-xs text-gray-500 mt-0.5 capitalize">
                {hook.label ?? "Fitness"}
              </p>
            </div>
            {hook.engagement_ratio > 0 && (
              <span className="text-xs bg-green-400/10 text-green-400 px-2 py-0.5 rounded-full shrink-0">
                {formatEngagement(hook.engagement_ratio)}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

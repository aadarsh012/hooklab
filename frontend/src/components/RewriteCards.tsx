"use client";

import type { HookRewrite } from "@/types/analysis";

interface Props {
  rewrites: HookRewrite[];
  onAdopt: (text: string) => void;
  currentScore: number;
}

interface RewriteStyle {
  labelClass: string;
  buttonClass: string;
  buttonBorder: string;
}

const STYLES: RewriteStyle[] = [
  {
    labelClass: "text-green-400",
    buttonClass: "text-green-400 hover:bg-green-400/5",
    buttonBorder: "border-green-500/50 hover:border-green-400",
  },
  {
    labelClass: "text-orange-400",
    buttonClass: "text-orange-400 hover:bg-orange-400/5",
    buttonBorder: "border-orange-500/50 hover:border-orange-400",
  },
];

const DIM_LABELS: Record<string, string> = {
  specificity: "Sharper & specific",
  curiosity_gap: "Bigger curiosity gap",
  clarity_of_payoff: "Clearer payoff",
  concreteness: "More concrete",
};

function dimLabel(dim: string): string {
  const key = dim.toLowerCase().replace(/\s+/g, "_");
  return DIM_LABELS[key] ?? dim;
}

export default function RewriteCards({ rewrites, onAdopt, currentScore }: Props) {
  const projected = [
    Math.min(100, currentScore + 35),
    Math.min(100, currentScore + 22),
  ];

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-5">
      <h3 className="font-semibold text-white mb-1">Two stronger versions</h3>
      <p className="text-sm text-gray-500 mb-4">
        Tap Adopt to pull one into your draft and keep iterating.
      </p>

      <div className="grid grid-cols-2 gap-4">
        {rewrites.slice(0, 2).map((rw, i) => {
          const style = STYLES[i % STYLES.length];
          return (
            <div
              key={i}
              className="bg-[#111] border border-[#2a2a2a] rounded-xl p-4 flex flex-col"
            >
              {/* Label + projected */}
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs font-semibold ${style.labelClass}`}>
                  {dimLabel(rw.target_dimension)}
                </span>
                <span className="text-xs text-gray-500">
                  projected ~{projected[i]}
                </span>
              </div>

              {/* Rewrite quote */}
              <p className="text-sm text-white font-medium leading-relaxed mb-2 flex-1">
                &ldquo;{rw.rewritten_hook}&rdquo;
              </p>

              {/* Explanation */}
              <p className="text-xs text-gray-500 mb-4">{rw.changes_made}</p>

              {/* Adopt button */}
              <button
                onClick={() => onAdopt(rw.rewritten_hook)}
                className={`w-full py-2 border rounded-lg text-sm font-medium transition-colors ${style.buttonClass} ${style.buttonBorder}`}
              >
                Adopt this →
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

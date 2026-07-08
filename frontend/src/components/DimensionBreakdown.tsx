import type { DimensionScore } from "@/types/analysis";

interface Props {
  dimensions: DimensionScore[];
}

interface DimConfig {
  label: string;
  scoreClass: string;
  barClass: string;
  defaultDesc: string;
}

const DIM_CONFIG: Record<string, DimConfig> = {
  specificity: {
    label: "Specificity",
    scoreClass: "text-green-400",
    barClass: "bg-green-500",
    defaultDesc: "Concrete details beat vague claims.",
  },
  curiosity_gap: {
    label: "Curiosity Gap",
    scoreClass: "text-orange-400",
    barClass: "bg-orange-500",
    defaultDesc: "Opens a loop the viewer needs to close.",
  },
  clarity_of_payoff: {
    label: "Clarity of Payoff",
    scoreClass: "text-yellow-400",
    barClass: "bg-yellow-500",
    defaultDesc: "They instantly know what they'll get.",
  },
  concreteness: {
    label: "Concreteness",
    scoreClass: "text-purple-400",
    barClass: "bg-purple-500",
    defaultDesc: "Tangible and easy to picture.",
  },
};

function toKey(dim: string): string {
  return dim.toLowerCase().replace(/\s+/g, "_");
}

export default function DimensionBreakdown({ dimensions }: Props) {
  const minScore = Math.min(...dimensions.map((d) => d.score));

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-5">
      <h3 className="font-semibold text-white mb-1">What's working, line by line</h3>
      <p className="text-sm text-gray-500 mb-5">
        Four things that decide whether people keep watching.
      </p>

      <div className="space-y-5">
        {dimensions.map((dim) => {
          const key = toKey(dim.dimension);
          const cfg = DIM_CONFIG[key];
          const displayScore = dim.score * 10;
          const isWeakest = dim.score === minScore;

          return (
            <div key={dim.dimension}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-semibold text-white text-sm">
                  {cfg?.label ?? dim.dimension}
                </span>
                <span className={`font-bold text-sm ${cfg?.scoreClass ?? "text-gray-400"}`}>
                  {displayScore}
                </span>
              </div>
              <div className="h-2 bg-[#2a2a2a] rounded-full mb-2 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${cfg?.barClass ?? "bg-gray-500"}`}
                  style={{ width: `${displayScore}%` }}
                />
              </div>
              <p className="text-xs text-gray-500">
                {cfg?.defaultDesc ?? ""}
                {dim.explanation && (
                  <span className="text-gray-400"> {dim.explanation}</span>
                )}
                {isWeakest && (
                  <span className="text-orange-400 font-medium ml-1">
                    This is the one to fix first.
                  </span>
                )}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

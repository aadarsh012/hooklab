const PUBLISH_THRESHOLD = 78;

interface Props {
  score: number;
  attemptCount: number;
}

function scoreColor(score: number): string {
  if (score < 40) return "#f97316";
  if (score < 60) return "#eab308";
  if (score < PUBLISH_THRESHOLD) return "#22d3ee";
  return "#4ade80";
}

function scoreLabel(score: number): string {
  if (score < 40) return "Needs a sharper first line";
  if (score < 60) return "Getting there";
  if (score < PUBLISH_THRESHOLD) return "Strong — keep refining";
  return "Publish-ready";
}

export default function StrengthGauge({ score, attemptCount }: Props) {
  const color = scoreColor(score);
  const label = scoreLabel(score);
  const ptsToGo = Math.max(0, PUBLISH_THRESHOLD - score);
  const progressPct = Math.min((score / PUBLISH_THRESHOLD) * 100, 100);

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-semibold tracking-widest text-gray-500 uppercase">
          Hook Strength
        </span>
        <span className="text-xs bg-[#2a2a2a] px-2 py-0.5 rounded text-gray-400">
          Attempt {attemptCount}
        </span>
      </div>

      {/* Semicircle gauge */}
      <div className="flex justify-center my-2">
        <svg viewBox="0 0 200 120" className="w-52">
          {/* Background track */}
          <path
            d="M 15 110 A 85 85 0 0 1 185 110"
            fill="none"
            stroke="#2a2a2a"
            strokeWidth="14"
            strokeLinecap="round"
          />
          {/* Value arc */}
          <path
            d="M 15 110 A 85 85 0 0 1 185 110"
            fill="none"
            stroke={color}
            strokeWidth="14"
            strokeLinecap="round"
            pathLength={100}
            strokeDasharray={100}
            strokeDashoffset={100 - score}
            style={{ transition: "stroke-dashoffset 0.6s ease" }}
          />
          {/* Score number */}
          <text
            x="100"
            y="82"
            textAnchor="middle"
            fill={color}
            fontSize="42"
            fontWeight="700"
            fontFamily="system-ui, sans-serif"
          >
            {score}
          </text>
          {/* "OUT OF 100" */}
          <text
            x="100"
            y="100"
            textAnchor="middle"
            fill="#6b7280"
            fontSize="9"
            fontFamily="system-ui, sans-serif"
            letterSpacing="2"
          >
            OUT OF 100
          </text>
        </svg>
      </div>

      <p className="text-center font-semibold text-base mb-1" style={{ color }}>
        {label}
      </p>
      <p className="text-center text-xs text-gray-500 mb-4">
        Totally normal — the rewrites below fix this fast.
      </p>

      {/* Progress to publish-ready */}
      {ptsToGo > 0 ? (
        <div className="bg-[#111] rounded-xl p-3">
          <div className="flex justify-between text-xs mb-2">
            <span className="text-gray-400">
              Reach {PUBLISH_THRESHOLD} to unlock publish-ready
            </span>
            <span className="font-medium" style={{ color }}>
              {ptsToGo} pts to go
            </span>
          </div>
          <div className="h-1.5 bg-[#2a2a2a] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${progressPct}%`, backgroundColor: color }}
            />
          </div>
        </div>
      ) : (
        <div className="bg-green-400/10 border border-green-400/20 rounded-xl p-3 text-center">
          <span className="text-green-400 text-sm font-medium">
            ✓ Publish-ready
          </span>
        </div>
      )}
    </div>
  );
}

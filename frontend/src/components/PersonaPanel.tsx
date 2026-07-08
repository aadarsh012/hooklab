import type { PersonaReaction } from "@/types/analysis";

interface Props {
  reactions: PersonaReaction[];
  niche: string;
}

const AVATAR_COLORS = ["bg-blue-700", "bg-teal-700", "bg-purple-700"];

export default function PersonaPanel({ reactions, niche }: Props) {
  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-5">
      <h3 className="font-semibold text-white mb-1">
        {reactions.length} viewers from {niche} reacted
      </h3>
      <p className="text-sm text-gray-500 mb-4">
        Simulated, but based on how real audiences in your niche behave.
      </p>

      <div className="grid grid-cols-3 gap-3">
        {reactions.map((r, i) => (
          <div
            key={r.persona_name}
            className="bg-[#111] border border-[#2a2a2a] rounded-xl p-4 flex flex-col"
          >
            {/* Avatar + name */}
            <div className="flex items-center gap-2 mb-3">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold shrink-0 ${AVATAR_COLORS[i % AVATAR_COLORS.length]}`}
              >
                {r.persona_name.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {r.persona_name}
                </p>
              </div>
            </div>

            {/* Would watch badge */}
            <div
              className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full mb-3 w-fit ${
                r.would_watch
                  ? "text-green-400 bg-green-400/10"
                  : "text-red-400 bg-red-400/10"
              }`}
            >
              <span>{r.would_watch ? "✓" : "×"}</span>
              <span>{r.would_watch ? "Would watch" : "Would scroll"}</span>
            </div>

            {/* Reaction quote */}
            <p className="text-xs text-gray-400 leading-relaxed">
              {r.reaction}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

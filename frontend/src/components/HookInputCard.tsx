"use client";

const NICHES = ["Fitness", "Finance", "Food", "Tech"];

interface Props {
  hookText: string;
  setHookText: (text: string) => void;
  selectedNiche: string;
  setSelectedNiche: (niche: string) => void;
  onAnalyze: () => void;
  loading: boolean;
  hasResult: boolean;
}

function wordFeedback(count: number): string {
  if (count === 0) return "";
  if (count < 4) return "too short — add more";
  if (count <= 8) return "a little more punch could help";
  if (count <= 15) return "solid length";
  return "try trimming it down";
}

export default function HookInputCard({
  hookText,
  setHookText,
  selectedNiche,
  setSelectedNiche,
  onAnalyze,
  loading,
  hasResult,
}: Props) {
  const wordCount = hookText.trim() ? hookText.trim().split(/\s+/).length : 0;

  return (
    <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-5">
      <h2 className="font-semibold text-white mb-1">Write your hook</h2>
      <p className="text-sm text-gray-500 mb-4">The first line that has to stop a thumb.</p>

      {/* Niche pills */}
      <div className="flex gap-2 flex-wrap mb-4">
        {NICHES.map((niche) => (
          <button
            key={niche}
            onClick={() => setSelectedNiche(niche)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedNiche === niche
                ? "bg-green-400 text-black"
                : "border border-[#3a3a3a] text-gray-400 hover:border-gray-500 hover:text-gray-200"
            }`}
          >
            {niche}
          </button>
        ))}
      </div>

      {/* Textarea */}
      <textarea
        value={hookText}
        onChange={(e) => setHookText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && e.metaKey) onAnalyze();
        }}
        placeholder="Type your hook here..."
        rows={4}
        className="w-full bg-[#111] border border-[#2a2a2a] rounded-xl p-3 text-white placeholder-gray-600 text-sm resize-none focus:outline-none focus:border-[#444] transition-colors"
      />

      {/* Word count */}
      {wordCount > 0 && (
        <div className="flex items-center justify-between mt-2 mb-1">
          <span className="text-xs text-orange-400">
            {wordCount} words · {wordFeedback(wordCount)}
          </span>
          <span className="text-xs text-gray-500 bg-[#222] border border-[#2a2a2a] px-2 py-0.5 rounded">
            {wordCount} words
          </span>
        </div>
      )}

      {/* Analyze button */}
      <button
        onClick={onAnalyze}
        disabled={!hookText.trim() || loading}
        className="w-full mt-4 py-3 bg-green-400 text-black font-semibold rounded-xl hover:bg-green-300 transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-sm"
      >
        {loading ? "Analyzing…" : hasResult ? "Re-analyze hook" : "Analyze hook"}
      </button>
    </div>
  );
}

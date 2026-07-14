"use client";

import { useState } from "react";
import Header from "@/components/Header";
import HookInputCard from "@/components/HookInputCard";
import StrengthGauge from "@/components/StrengthGauge";
import DimensionBreakdown from "@/components/DimensionBreakdown";
import PersonaPanel from "@/components/PersonaPanel";
import RewriteCards from "@/components/RewriteCards";
import SimilarHooks from "@/components/SimilarHooks";
import { analyzeHook } from "@/lib/api";
import type { AnalysisResult } from "@/types/analysis";

function computeStrengthScore(result: AnalysisResult): number {
  const { label, confidence } = result.score_breakdown;
  const raw = label === "strong" ? confidence * 100 : (1 - confidence) * 100;
  return Math.round(raw);
}

export default function Home() {
  const [hookText, setHookText] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [attemptCount, setAttemptCount] = useState(0);
  const [selectedNiche, setSelectedNiche] = useState("Fitness");
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    if (!hookText.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeHook(hookText);
      setResult(data);
      setAttemptCount((c) => c + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  function handleAdopt(text: string) {
    setHookText(text);
  }

  const strengthScore = result ? computeStrengthScore(result) : null;

  return (
    <div className="min-h-screen lg:h-screen bg-[#111111] text-white flex flex-col lg:overflow-hidden">
      <Header />

      <div className="flex-1 lg:overflow-hidden">
        <div className="h-full max-w-[1400px] mx-auto px-6 py-8 flex flex-col lg:flex-row gap-5">
          {/* Left column */}
          <div className="lg:w-[360px] shrink-0 space-y-4 lg:min-h-0 lg:overflow-y-auto lg:pb-8">
            <HookInputCard
              hookText={hookText}
              setHookText={setHookText}
              selectedNiche={selectedNiche}
              setSelectedNiche={setSelectedNiche}
              onAnalyze={handleAnalyze}
              loading={loading}
              hasResult={!!result}
            />
            {result && strengthScore !== null && (
              <StrengthGauge score={strengthScore} attemptCount={attemptCount} />
            )}
          </div>

          {/* Right column */}
          <div className="flex-1 lg:min-h-0 lg:overflow-y-auto space-y-4 pb-8">
            {error && (
              <div className="bg-red-900/20 border border-red-700/40 rounded-2xl p-5 text-red-400 text-sm">
                {error}
              </div>
            )}

            {loading && !result && (
              <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-10 flex items-center justify-center">
                <div className="text-gray-500 text-sm">Analyzing your hook…</div>
              </div>
            )}

            {result && (
              <>
                <DimensionBreakdown dimensions={result.score_breakdown.dimension_scores} />
                <PersonaPanel reactions={result.persona_reactions} niche={selectedNiche} />
                {result.rewrites.length > 0 && strengthScore !== null && (
                  <RewriteCards
                    rewrites={result.rewrites}
                    onAdopt={handleAdopt}
                    currentScore={strengthScore}
                  />
                )}
                {result.similar_hooks.length > 0 && (
                  <SimilarHooks hooks={result.similar_hooks} />
                )}
              </>
            )}

            {!result && !loading && !error && (
              <div className="flex items-center justify-center h-64 text-gray-600 text-sm">
                Write a hook on the left to see the analysis here.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

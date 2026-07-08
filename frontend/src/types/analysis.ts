export type EngagementLabel = "strong" | "weak";

export interface DimensionScore {
  dimension: string;
  score: number; // 1-10
  explanation: string;
}

export interface ScoreBreakdown {
  label: EngagementLabel;
  confidence: number; // 0.0-1.0
  dimension_scores: DimensionScore[];
}

export interface SimilarHook {
  hook_text: string;
  label: string | null;
  engagement_ratio: number;
  distance: number;
}

export interface PersonaReaction {
  persona_name: string;
  would_watch: boolean;
  reaction: string;
  reasoning: string;
}

export interface HookRewrite {
  rewritten_hook: string;
  changes_made: string;
  target_dimension: string;
}

export interface AnalysisResult {
  hook_text: string;
  score_breakdown: ScoreBreakdown;
  similar_hooks: SimilarHook[];
  persona_reactions: PersonaReaction[];
  rewrites: HookRewrite[];
}

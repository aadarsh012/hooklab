import type { AnalysisResult } from "@/types/analysis";
import { nextApiClientService } from "@/lib/nextApiClientService";

export async function analyzeHook(hookText: string): Promise<AnalysisResult> {
  return nextApiClientService.analyze(hookText);
}

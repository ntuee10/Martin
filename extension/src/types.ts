export interface Suggestion {
  id: string;
  type: 'grammar' | 'clarity' | 'specificity' | 'structure' | 'token_optimization' | 'technical_accuracy';
  original: string;
  suggested: string;
  confidence: number;
  explanation: string;
  tokenDelta: number;
  position: [number, number];
  developerTip?: string;
  codeExample?: string;
}

export interface PromptMetrics {
  clarityScore: number;
  specificityScore: number;
  tokenEfficiency: number;
  technicalAccuracy: number;
  estimatedQualityImprovement: number;
  tokenCount: number;
  estimatedCost: number;
}

export interface AnalysisResponse {
  suggestions: Suggestion[];
  metrics: PromptMetrics;
  processingTimeMs: number;
  cacheHit: boolean;
  modelSpecificTips: string[];
}

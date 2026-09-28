export interface DetectResult {
  label: string;
  score: number;
  confidence: string;
  rationale: string;
  detailed_analysis: string;
  key_indicators: string[];
  methodology: string;
}

export interface DetectResponse {
  result: DetectResult;
}

export interface SkillItem {
  skill: string;
  contribution: number;
  evidence?: {
    tenure_years?: number;
    months_since_last_use?: number;
  };
}

export interface GapItem {
  skill: string;
  required: boolean;
}

export interface ClusterAlignment {
  cluster: string;
  align_pct: number;
  best_examples?: string[];
  gaps?: string[];
}

export interface ScoreResponse {
  score: number;
  label: string;
  best_fit: SkillItem[];
  gaps: GapItem[];
  clusters: ClusterAlignment[];
  terms: Record<string, number>;
  rewrites?: string[];
}

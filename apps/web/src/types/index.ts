export interface User {
  id: string;
  email: string;
  wallet_address: string;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type InvestigationStatus = "pending" | "running" | "completed" | "failed";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type ValidatorType =
  | "identity"
  | "github"
  | "funding"
  | "onchain"
  | "security";

export type ValidatorStatus = "pending" | "running" | "completed" | "failed";

export interface Validator {
  id: string;
  investigation_id: string;
  validator_type: ValidatorType;
  status: ValidatorStatus;
  findings: string | null;
  confidence_score: number | null;
  sources: string[] | null;
  created_at: string;
}

export interface Claim {
  claim: string;
  evidence: string;
  source?: string;
  confidence: number;
}

export interface ReportScores {
  overall: number;
  team: number;
  funding: number;
  product: number;
  github: number;
  community: number;
  tokenomics: number;
  security: number;
  onchain: number;
  reputation: number;
}

export interface Report {
  id: string;
  investigation_id: string;
  scores: ReportScores;
  risk_level: RiskLevel;
  consensus_result: Record<string, unknown>;
  evidence: Record<string, unknown>;
  verified_claims: Claim[];
  disputed_claims: Claim[];
  unresolved_claims: Claim[];
  summary: string;
  recommendation: string;
  created_at: string;
}

export interface Investigation {
  id: string;
  user_id: string;
  protocol_name: string;
  status: InvestigationStatus;
  contract_address: string | null;
  tx_hash: string | null;
  created_at: string;
  completed_at: string | null;
  validators: Validator[];
  report: Report | null;
}

export interface SSEEvent {
  type: "validator_update" | "progress" | "completed" | "failed" | "ping";
  data: {
    validator_type?: ValidatorType;
    status?: ValidatorStatus;
    findings?: string;
    confidence_score?: number;
    progress?: number;
    message?: string;
    report?: Report;
  };
}

export interface EvidenceItem {
  source: string;
  data_type: string;
  summary: string;
  fetched_at: string;
  url?: string;
}

export const VALIDATOR_LABELS: Record<ValidatorType, string> = {
  identity: "Identity Verification",
  github: "GitHub Activity",
  funding: "Funding Verification",
  onchain: "On-chain Activity",
  security: "Security Audit",
};

export const VALIDATOR_ICONS: Record<ValidatorType, string> = {
  identity: "shield",
  github: "git-branch",
  funding: "dollar-sign",
  onchain: "link",
  security: "lock",
};

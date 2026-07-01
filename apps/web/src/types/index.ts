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
  | "founders"
  | "funding"
  | "investors"
  | "github"
  | "documentation"
  | "onchain"
  | "tokenomics"
  | "security"
  | "community"
  | "ecosystem"
  | "product"
  | "media";

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
  founders: "Founder History",
  funding: "Funding Verification",
  investors: "Investor Reputation",
  github: "GitHub Activity",
  documentation: "Documentation",
  onchain: "On-chain Activity",
  tokenomics: "Tokenomics",
  security: "Security Audit",
  community: "Community Health",
  ecosystem: "Ecosystem Integrations",
  product: "Product Verification",
  media: "Media & Claims",
};

export const VALIDATOR_ICONS: Record<ValidatorType, string> = {
  identity: "shield",
  founders: "users",
  funding: "dollar-sign",
  investors: "briefcase",
  github: "git-branch",
  documentation: "file-text",
  onchain: "link",
  tokenomics: "coins",
  security: "lock",
  community: "message-circle",
  ecosystem: "globe",
  product: "package",
  media: "radio",
};

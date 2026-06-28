from pydantic import BaseModel
from typing import Optional


class CreateInvestigationRequest(BaseModel):
    protocol_name: str


class ValidatorResponse(BaseModel):
    id: str
    investigation_id: str
    validator_type: str
    status: str
    findings: Optional[str]
    confidence_score: Optional[float]
    sources: Optional[list]
    created_at: str

    class Config:
        from_attributes = True


class ScoresResponse(BaseModel):
    overall: float
    team: float
    funding: float
    product: float
    github: float
    community: float
    tokenomics: float
    security: float
    onchain: float
    reputation: float


class ClaimResponse(BaseModel):
    claim: str
    evidence: Optional[str] = None
    source: Optional[str] = None
    confidence: Optional[float] = None


class ReportResponse(BaseModel):
    id: str
    investigation_id: str
    scores: ScoresResponse
    risk_level: str
    consensus_result: Optional[dict]
    evidence: Optional[dict]
    verified_claims: Optional[list]
    disputed_claims: Optional[list]
    unresolved_claims: Optional[list]
    summary: Optional[str]
    recommendation: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class InvestigationResponse(BaseModel):
    id: str
    user_id: str
    protocol_name: str
    status: str
    contract_address: Optional[str]
    tx_hash: Optional[str]
    created_at: str
    completed_at: Optional[str]
    validators: list[ValidatorResponse] = []
    report: Optional[ReportResponse] = None

    class Config:
        from_attributes = True

import asyncio
import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse
from ..core.database import get_db
from ..core.deps import get_current_user
from ..core.security import decode_token
from ..models.user import User
from ..models.investigation import Investigation, Validator, Report
from ..schemas.investigation import CreateInvestigationRequest, InvestigationResponse, ReportResponse, ScoresResponse
from ..collectors import collect_all_evidence
from ..services.genlayer_service import run_investigation_via_genlayer, VALIDATOR_TYPES
from ..services.email_service import send_investigation_complete_email

router = APIRouter(prefix="/investigations", tags=["investigations"])


def _report_to_response(report: Report) -> ReportResponse:
    scores = ScoresResponse(
        overall=float(report.overall_score),
        team=float(report.team_score),
        funding=float(report.funding_score),
        product=float(report.product_score),
        github=float(report.github_score),
        community=float(report.community_score),
        tokenomics=float(report.tokenomics_score),
        security=float(report.security_score),
        onchain=float(report.onchain_score),
        reputation=float(report.reputation_score),
    )
    return ReportResponse(
        id=report.id,
        investigation_id=report.investigation_id,
        scores=scores,
        risk_level=report.risk_level,
        consensus_result=report.consensus_result,
        evidence=report.evidence,
        verified_claims=report.verified_claims,
        disputed_claims=report.disputed_claims,
        unresolved_claims=report.unresolved_claims,
        summary=report.summary,
        recommendation=report.recommendation,
        created_at=report.created_at.isoformat(),
    )


def _inv_to_response(inv: Investigation) -> dict:
    validators = [
        {
            "id": v.id,
            "investigation_id": v.investigation_id,
            "validator_type": v.validator_type,
            "status": v.status,
            "findings": v.findings,
            "confidence_score": float(v.confidence_score) if v.confidence_score else None,
            "sources": v.sources,
            "created_at": v.created_at.isoformat(),
        }
        for v in (inv.validators or [])
    ]
    return {
        "id": inv.id,
        "user_id": inv.user_id,
        "protocol_name": inv.protocol_name,
        "status": inv.status,
        "contract_address": inv.contract_address,
        "tx_hash": inv.tx_hash,
        "created_at": inv.created_at.isoformat(),
        "completed_at": inv.completed_at.isoformat() if inv.completed_at else None,
        "validators": validators,
        "report": _report_to_response(inv.report).model_dump() if inv.report else None,
    }


@router.post("", status_code=201)
async def create_investigation(
    req: CreateInvestigationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = Investigation(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        protocol_name=req.protocol_name.strip(),
        status="pending",
    )
    db.add(inv)

    # Create validator placeholders
    for vtype in VALIDATOR_TYPES:
        v = Validator(
            id=str(uuid.uuid4()),
            investigation_id=inv.id,
            validator_type=vtype,
            status="pending",
        )
        db.add(v)

    await db.commit()
    await db.refresh(inv)

    background_tasks.add_task(
        _run_investigation_background,
        inv.id,
        req.protocol_name,
        current_user.id,
        current_user.email,
        current_user.encrypted_private_key,
    )

    result = await db.execute(
        select(Investigation)
        .options(selectinload(Investigation.validators), selectinload(Investigation.report))
        .where(Investigation.id == inv.id)
    )
    full_inv = result.scalar_one()
    return _inv_to_response(full_inv)


async def _run_investigation_background(
    investigation_id: str,
    protocol_name: str,
    user_id: str,
    user_email: str,
    encrypted_private_key: str = None,
):
    from ..core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Update status to running
            result = await db.execute(select(Investigation).where(Investigation.id == investigation_id))
            inv = result.scalar_one()
            inv.status = "running"
            await db.commit()

            # Collect evidence
            evidence = await collect_all_evidence(protocol_name)

            # Decrypt the user's wallet private key for signing
            user_private_key = None
            if encrypted_private_key:
                from ..core.security import decrypt_private_key
                try:
                    user_private_key = decrypt_private_key(encrypted_private_key)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Failed to decrypt user wallet, using service account: {e}")

            # Run GenLayer investigation
            final_report_data = None
            async for event in run_investigation_via_genlayer(protocol_name, evidence, investigation_id, user_private_key=user_private_key):
                if event["type"] == "validator_update":
                    result = await db.execute(
                        select(Validator).where(
                            Validator.investigation_id == investigation_id,
                            Validator.validator_type == event["validator_type"],
                        )
                    )
                    v = result.scalar_one_or_none()
                    if v:
                        v.status = event.get("status", "running")
                        if event.get("findings"):
                            v.findings = event["findings"]
                        if event.get("confidence_score"):
                            v.confidence_score = event["confidence_score"]
                        if event.get("sources") is not None:
                            v.sources = event["sources"]
                        if event.get("verified_claims") is not None:
                            v.verified_claims = event["verified_claims"]
                        if event.get("disputed_claims") is not None:
                            v.disputed_claims = event["disputed_claims"]
                        await db.commit()

                elif event["type"] == "completed":
                    final_report_data = event["report"]
                    # Persist tx_hash on the investigation row
                    tx_hash = (final_report_data.get("consensus_result") or {}).get("tx_hash")
                    if tx_hash:
                        result = await db.execute(select(Investigation).where(Investigation.id == investigation_id))
                        inv_row = result.scalar_one()
                        inv_row.tx_hash = tx_hash
                        await db.commit()

            # Save report
            if final_report_data:
                scores = final_report_data.get("scores", {})
                report = Report(
                    id=str(uuid.uuid4()),
                    investigation_id=investigation_id,
                    overall_score=scores.get("overall", 0),
                    team_score=scores.get("team", 0),
                    funding_score=scores.get("funding", 0),
                    product_score=scores.get("product", 0),
                    github_score=scores.get("github", 0),
                    community_score=scores.get("community", 0),
                    tokenomics_score=scores.get("tokenomics", 0),
                    security_score=scores.get("security", 0),
                    onchain_score=scores.get("onchain", 0),
                    reputation_score=scores.get("reputation", 0),
                    risk_level=final_report_data.get("risk_level", "unknown"),
                    consensus_result=final_report_data.get("consensus_result"),
                    evidence=evidence,
                    verified_claims=final_report_data.get("verified_claims"),
                    disputed_claims=final_report_data.get("disputed_claims"),
                    unresolved_claims=final_report_data.get("unresolved_claims"),
                    summary=final_report_data.get("summary"),
                    recommendation=final_report_data.get("recommendation"),
                )
                db.add(report)

                result = await db.execute(select(Investigation).where(Investigation.id == investigation_id))
                inv = result.scalar_one()
                inv.status = "completed"
                inv.completed_at = datetime.now(timezone.utc)
                await db.commit()

                # Send email
                send_investigation_complete_email(
                    user_email,
                    protocol_name,
                    scores.get("overall", 0),
                    final_report_data.get("risk_level", "unknown"),
                    investigation_id,
                )

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Investigation failed: {e}")
            async with AsyncSessionLocal() as db2:
                result = await db2.execute(select(Investigation).where(Investigation.id == investigation_id))
                inv = result.scalar_one_or_none()
                if inv:
                    inv.status = "failed"
                    await db2.commit()


@router.get("")
async def list_investigations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Investigation)
        .options(selectinload(Investigation.validators), selectinload(Investigation.report))
        .where(Investigation.user_id == current_user.id)
        .order_by(Investigation.created_at.desc())
    )
    return [_inv_to_response(inv) for inv in result.scalars().all()]


@router.get("/{investigation_id}")
async def get_investigation(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Investigation)
        .options(selectinload(Investigation.validators), selectinload(Investigation.report))
        .where(Investigation.id == investigation_id, Investigation.user_id == current_user.id)
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return _inv_to_response(inv)


@router.get("/{investigation_id}/stream")
async def stream_investigation(
    investigation_id: str,
    request: Request,
    token: str = None,
    db: AsyncSession = Depends(get_db),
):
    # Validate token from query param (SSE can't set headers)
    user_id = decode_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    from ..core.database import AsyncSessionLocal

    async def event_generator():
        last_statuses = {}
        for _ in range(300):  # max 5 min polling
            if await request.is_disconnected():
                break

            async with AsyncSessionLocal() as poll_db:
                result = await poll_db.execute(
                    select(Investigation)
                    .options(selectinload(Investigation.validators), selectinload(Investigation.report))
                    .where(Investigation.id == investigation_id, Investigation.user_id == user_id)
                )
                inv = result.scalar_one_or_none()
                if not inv:
                    break

                for v in inv.validators:
                    if last_statuses.get(v.validator_type) != v.status:
                        last_statuses[v.validator_type] = v.status
                        yield {
                            "data": json.dumps({
                                "type": "validator_update",
                                "data": {
                                    "validator_type": v.validator_type,
                                    "status": v.status,
                                    "findings": v.findings,
                                    "confidence_score": float(v.confidence_score) if v.confidence_score else None,
                                },
                            })
                        }

                if inv.status in ("completed", "failed"):
                    yield {
                        "data": json.dumps({
                            "type": inv.status,
                            "data": {"message": f"Investigation {inv.status}"},
                        })
                    }
                    break

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

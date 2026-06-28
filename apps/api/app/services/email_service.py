import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from ..core.config import settings

logger = logging.getLogger(__name__)


def _get_api():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.BREVO_API_KEY
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


def send_welcome_email(to_email: str, wallet_address: str):
    try:
        api = _get_api()
        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
            subject="Welcome to TrustLayer — Your Wallet is Ready",
            html_content=f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; background: #080B14; color: #E2E8F0; padding: 40px; border-radius: 16px;">
                <img src="https://trust-layer.vercel.app/icon.png" width="48" style="margin-bottom: 24px;" />
                <h1 style="color: #E2E8F0; font-size: 24px; margin-bottom: 8px;">Welcome to TrustLayer</h1>
                <p style="color: #94A3B8; margin-bottom: 24px;">Your account has been created and a blockchain wallet has been automatically generated for you.</p>
                <div style="background: #0D1117; border: 1px solid #1C2333; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
                    <div style="color: #64748B; font-size: 12px; font-family: monospace; margin-bottom: 8px;">YOUR WALLET ADDRESS</div>
                    <div style="color: #10B981; font-family: monospace; font-size: 13px; word-break: break-all;">{wallet_address}</div>
                </div>
                <p style="color: #94A3B8; font-size: 14px;">Your private key is encrypted and stored securely. You can export it any time from your account settings.</p>
                <a href="https://trust-layer.vercel.app/dashboard" style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: 600; margin-top: 24px;">
                    Go to Dashboard →
                </a>
            </div>
            """,
        )
        api.send_transac_email(email)
    except ApiException as e:
        logger.error(f"Failed to send welcome email: {e}")


def send_investigation_complete_email(to_email: str, protocol_name: str, trust_score: float, risk_level: str, investigation_id: str):
    try:
        api = _get_api()
        score_color = "#10B981" if trust_score >= 75 else "#F59E0B" if trust_score >= 50 else "#EF4444"
        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
            subject=f"Investigation Complete: {protocol_name} — Trust Score {trust_score:.1f}",
            html_content=f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; background: #080B14; color: #E2E8F0; padding: 40px; border-radius: 16px;">
                <img src="https://trust-layer.vercel.app/icon.png" width="48" style="margin-bottom: 24px;" />
                <h1 style="color: #E2E8F0; font-size: 22px;">Investigation Complete</h1>
                <p style="color: #94A3B8;">Your TrustLayer investigation for <strong style="color: white;">{protocol_name}</strong> has finished.</p>
                <div style="background: #0D1117; border: 1px solid #1C2333; border-radius: 12px; padding: 24px; margin: 24px 0; text-align: center;">
                    <div style="font-size: 56px; font-weight: bold; color: {score_color};">{trust_score:.1f}</div>
                    <div style="color: #64748B; font-size: 14px;">Trust Score</div>
                    <div style="color: {score_color}; margin-top: 8px; text-transform: uppercase; font-size: 12px; font-family: monospace;">{risk_level} RISK</div>
                </div>
                <a href="https://trust-layer.vercel.app/investigations/{investigation_id}" style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: 600;">
                    View Full Report →
                </a>
            </div>
            """,
        )
        api.send_transac_email(email)
    except ApiException as e:
        logger.error(f"Failed to send investigation email: {e}")

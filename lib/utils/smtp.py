import aiosmtplib
from email.message import EmailMessage
from typing import List, Optional
from lib.config.settings import settings  

# Example settings expected in settings:
# SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_USE_TLS (bool), SMTP_FROM_EMAIL, SMTP_FROM_NAME

async def send_email(
    subject: str,
    recipients: List[str],
    body: str,
    html: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None,
) -> dict:
    """
    Send an email asynchronously via SMTP (aiosmtplib).

    Returns a dict with status and info or raises Exception on failure.
    """
    if not recipients:
        raise ValueError("At least one recipient is required")

    sender_email = sender_email or getattr(settings, "SMTP_FROM_EMAIL", None)
    sender_name = sender_name or getattr(settings, "SMTP_FROM_NAME", None)

    if not sender_email:
        raise ValueError("SMTP_FROM_EMAIL must be set in your settings")

    # Build message
    msg = EmailMessage()
    from_field = f"{sender_name} <{sender_email}>" if sender_name else sender_email
    msg["From"] = from_field
    msg["To"] = ", ".join(recipients)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        # bcc is not placed in headers (but we include in recipients list)
        pass
    msg["Subject"] = subject
    msg.set_content(body)

    if html:
        msg.add_alternative(html, subtype="html")

    # Full recipient list (To + Cc + Bcc)
    envelope_recipients = list(recipients)
    if cc:
        envelope_recipients += cc
    if bcc:
        envelope_recipients += bcc

    host = getattr(settings, "SMTP_HOST", None)
    port = getattr(settings, "SMTP_PORT", None)
    user = getattr(settings, "SMTP_USER", None)
    password = getattr(settings, "SMTP_PASSWORD", None)
    use_tls = getattr(settings, "SMTP_USE_TLS", True)

    if not host or not port:
        raise ValueError("SMTP_HOST and SMTP_PORT must be configured in settings")

    try:
        # Connect and send
        smtp_kwargs = dict(hostname=host, port=int(port))
        if use_tls:
            smtp_kwargs["start_tls"] = True

        smtp_client = aiosmtplib.SMTP(**smtp_kwargs)
        await smtp_client.connect()
        if user and password:
            await smtp_client.login(user, password)

        await smtp_client.send_message(msg, recipients=envelope_recipients, sender=sender_email)
        await smtp_client.quit()

        return {"success": True, "message": "Email sent", "recipients": envelope_recipients}
    except Exception as exc:
        # Bubble up or wrap error
        raise

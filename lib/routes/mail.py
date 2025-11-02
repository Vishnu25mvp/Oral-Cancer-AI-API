# lib/routers/mail_router.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional

from lib.config.database import get_async_session  # only if needed
from lib.utils import success_response, error_response, send_email  
from lib.config.settings import settings

router = APIRouter(prefix="/mail", tags=["Mail"])
templates = Jinja2Templates(directory="templates")  # ensure templates/ exists at project root


@router.get("/", response_class=HTMLResponse)
async def mail_ui(request: Request):
    """
    Render the simple UI for sending mail (GET /mail).
    """
    return templates.TemplateResponse("send_mail.html", {"request": request, "from_email": settings.SMTP_FROM_EMAIL})


@router.post("/send")
async def send_mail_api(
    request: Request,
    subject: str = Form(None),
    body: str = Form(None),
    html: Optional[str] = Form(None),
    to: str = Form(None),
    cc: Optional[str] = Form(None),
    bcc: Optional[str] = Form(None),
):
    """
    Accepts form POST from UI. Also works if you post JSON (use /mail/send-json below).
    `to`, `cc`, `bcc` are comma-separated lists.
    """
    # Normalize recipients
    if not to:
        return error_response("Recipient(s) `to` is required", status_code=400)

    recipients = [r.strip() for r in to.split(",") if r.strip()]
    cc_list = [r.strip() for r in cc.split(",")] if cc else None
    bcc_list = [r.strip() for r in bcc.split(",")] if bcc else None

    try:
        result = await send_email(
            subject=subject or "(no subject)",
            recipients=recipients,
            body=body or "",
            html=html,
            cc=cc_list,
            bcc=bcc_list,
        )
        return success_response(data=result, message="Email queued/sent")
    except Exception as e:
        return error_response("Failed to send email", details={"error": str(e)}, status_code=500)


# Optional JSON API
@router.post("/send-json")
async def send_mail_json(payload: dict):
    """
    JSON body:
    {
      "subject": "...",
      "body": "...",
      "html": "<b>...</b>",
      "to": ["a@x.com", "b@x.com"],
      "cc": [...],
      "bcc": [...]
    }
    """
    try:
        subject = payload.get("subject", "(no subject)")
        body = payload.get("body", "")
        html = payload.get("html")
        to = payload.get("to", [])
        cc = payload.get("cc")
        bcc = payload.get("bcc")

        if not to:
            return error_response("`to` must be provided as a list of emails", status_code=400)

        result = await send_email(subject, to, body, html=html, cc=cc, bcc=bcc)
        return success_response(data=result, message="Email sent")
    except Exception as e:
        return error_response("Failed to send email", details={"error": str(e)}, status_code=500)

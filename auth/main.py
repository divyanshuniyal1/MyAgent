# auth/main.py

import logging
from starlette.requests import Request
from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from urllib.parse import urlencode
from auth.sso import exchange_code_for_tokens, validate_id_token
from auth.jwt_utils import create_access_token
from memory.db import get_db
from memory.models import User
from config_settings import get_settings

logger = logging.getLogger("sso.auth")

app = FastAPI()

_LOGIN_PAGE = """<!DOCTYPE html><html><head><title>SSO Login</title>
<style>body{{font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#f0f2f5}}
.card{{background:#fff;border-radius:8px;padding:40px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,.15);max-width:420px;width:90%}}
h2{{color:#333;margin-bottom:8px}}p{{color:#666;margin-bottom:24px;font-size:14px}}
a.btn{{display:inline-block;background:#0078d4;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:600;font-size:15px}}
a.btn:hover{{background:#005a9e}}</style></head>
<body><div class="card">
<h2>&#128274; Microsoft SSO Login</h2>
<p>Click the button below to sign in with your Microsoft account.</p>
<a class="btn" href="{login_url}">Sign in with Microsoft</a>
</div></body></html>"""

_SUCCESS_PAGE = """<!DOCTYPE html><html><head><title>Login Successful</title>
<style>body{{font-family:sans-serif;background:#f0f2f5;padding:30px;margin:0}}
.card{{background:#fff;border-radius:8px;padding:30px;box-shadow:0 2px 12px rgba(0,0,0,.15);max-width:720px;margin:auto}}
h2{{color:#107c10;margin-top:0}}.info{{display:grid;gap:6px;margin-bottom:20px}}
.row{{display:flex;gap:10px}}.lbl{{font-weight:600;min-width:70px;color:#333}}.val{{color:#555}}
pre{{background:#1e1e1e;color:#d4d4d4;padding:16px;border-radius:6px;word-break:break-all;white-space:pre-wrap;font-size:13px;margin:0}}
.copy{{background:#0078d4;color:#fff;border:none;padding:7px 16px;border-radius:4px;cursor:pointer;font-size:13px;margin-bottom:10px}}
.copy:hover{{background:#005a9e}}code{{background:#eee;padding:2px 6px;border-radius:3px;font-size:13px}}</style></head>
<body><div class="card">
<h2>&#10003; Login Successful!</h2>
<div class="info">
<div class="row"><span class="lbl">Name</span><span class="val">{name}</span></div>
<div class="row"><span class="lbl">Email</span><span class="val">{email}</span></div>
</div>
<button class="copy" onclick="navigator.clipboard.writeText(document.getElementById('tk').innerText);this.innerText='&#10003; Copied!'">&#128203; Copy JWT Token</button>
<pre id="tk">{token}</pre>
</div></body></html>"""


def build_jwt_payload(claims: dict) -> dict:
    return {
        "sub": claims.get("oid", claims.get("sub", "")),
        "name": claims.get("name", ""),
        "email": claims.get("preferred_username", claims.get("email", "")),
        "roles": claims.get("roles", []),
    }


@app.get("/auth/login/microsoft")
async def microsoft_login(request: Request):
    settings = get_settings()
    params = urlencode({
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "response_mode": "query",
        "scope": "openid profile email",
    })
    login_url = (
        f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}"
        f"/oauth2/v2.0/authorize?{params}"
    )
    sec_fetch_mode = request.headers.get("sec-fetch-mode", "")
    if sec_fetch_mode == "navigate":
        return RedirectResponse(login_url)
    return HTMLResponse(_LOGIN_PAGE.format(login_url=login_url))


@app.get("/api/v1/auth/sso/azure/callback")
async def microsoft_callback(
    request: Request,
    code: str = None,
    error: str = None,
    error_description: str = "",
    db=Depends(get_db)
):
    if error:
        logger.error("Azure AD error: %s — %s", error, error_description)
        return JSONResponse({"detail": f"Azure AD error: {error} — {error_description}"}, status_code=400)
    if not code:
        return JSONResponse({"detail": "Authorization code missing"}, status_code=400)

    try:
        tokens = await exchange_code_for_tokens(code)
        id_token = tokens.get("id_token")
        if not id_token:
            return JSONResponse({"detail": "No id_token received from Azure AD"}, status_code=502)
        claims = validate_id_token(id_token)
    except Exception as exc:
        logger.exception("SSO callback failed")
        return JSONResponse({"detail": str(exc)}, status_code=401)

    payload = build_jwt_payload(claims)

    # Save/fetch user from DB and use DB integer id as sub
    user = db.query(User).filter_by(email=payload["email"]).first()
    if not user:
        user = User(email=payload["email"], name=payload["name"])
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    logger.info("SSO login successful for: %s", payload.get("email"))

    return HTMLResponse(_SUCCESS_PAGE.format(
        name=payload.get("name", ""),
        email=payload.get("email", ""),
        token=token,
    ))
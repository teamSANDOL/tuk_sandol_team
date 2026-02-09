# app.py
import os, time, secrets, hashlib, base64
from urllib.parse import urlencode

import jwt
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

app = FastAPI()
JWT_SECRET = os.getenv("LIT_JWT_SECRET", "change-me")  # 반드시 환경변수로
LIT_TTL = int(os.getenv("LIT_TTL_SECONDS", "90"))
KC_AUTH = os.getenv("KC_AUTH", "https://auth.example.com/realms/realm")
KC_CLIENT_ID = os.getenv("KC_CLIENT_ID", "my-client")
CALLBACK_URL = os.getenv("CALLBACK_URL", "https://auth.example.com/oidc/callback")
BASE_URL = os.getenv("BASE_URL", "https://auth.example.com")
JWT_ISS, JWT_AUD = "bot-link", "kc-init"


def pkce(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


@app.post("/bot/login-link")
async def bot_login_link(body: dict, request: Request):
    platform = (body.get("platform") or "").lower()
    ext_user_id = str(body.get("user_id") or "")
    if platform not in {"kakao", "discord", "telegram"} or not ext_user_id:
        raise HTTPException(400, "platform_or_user_id_missing")

    ua = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    fp = hashlib.sha256(f"{platform}|{ext_user_id}|{ua}|{ip}".encode()).hexdigest()[:16]

    now = int(time.time())
    lit = jwt.encode(
        {
            "iss": JWT_ISS,
            "aud": JWT_AUD,
            "iat": now,
            "nbf": now,
            "exp": now + LIT_TTL,
            "jti": secrets.token_urlsafe(16),
            "platform": platform,
            "ext_user_id": ext_user_id,
            "fp": fp,
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    return JSONResponse(
        {"login_url": f"{BASE_URL}/oidc/init?lit={lit}", "expires_in": LIT_TTL}
    )


@app.get("/oidc/init")
async def oidc_init(lit: str, request: Request):
    try:
        data = jwt.decode(
            lit, JWT_SECRET, algorithms=["HS256"], audience=JWT_AUD, issuer=JWT_ISS
        )
    except jwt.PyJWTError:
        raise HTTPException(400, "invalid_or_expired_lit")

    ua = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    fp_now = hashlib.sha256(
        f"{data['platform']}|{data['ext_user_id']}|{ua}|{ip}".encode()
    ).hexdigest()[:16]
    if fp_now != data.get("fp"):
        raise HTTPException(400, "fingerprint_mismatch")

    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = pkce(code_verifier)
    # state/nonce/code_verifier 저장은 최소 파일/메모리라도 구성 권장(생략 가능하나 실서비스에선 필요)

    params = {
        "client_id": KC_CLIENT_ID,
        "redirect_uri": CALLBACK_URL,
        "response_type": "code",
        "scope": "openid profile email",
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        # 필요 시 외부 IdP 고정: "kc_idp_hint": data["platform"]
    }
    return RedirectResponse(
        f"{KC_AUTH}/protocol/openid-connect/auth?{urlencode(params)}"
    )

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import httpx
import os
from typing import Optional

app = FastAPI(title="Temporary Web Service for SSO Testing")

# Keycloak 설정 (환경변수로 설정 가능)
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL", "http://localhost:8010/auth")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "sandol")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "temp-web-service")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "your-client-secret")

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        return None
    
    try:
        # JWT 토큰 검증 (간단한 구현)
        # 실제 환경에서는 Keycloak의 공개키로 검증해야 함
        token = credentials.credentials
        # 여기서는 토큰이 있으면 유효하다고 가정 (테스트용)
        return {"token": token}
    except Exception:
        return None

@app.get("/", response_class=HTMLResponse)
async def home(user = Depends(get_current_user)):
    if user:
        return f"""
        <html>
            <head><title>Temporary Web Service</title></head>
            <body>
                <h1>Welcome to Temporary Web Service</h1>
                <p>You are logged in!</p>
                <p>Token: {user['token'][:50]}...</p>
                <a href="/logout">Logout</a>
                <br><br>
                <a href="/protected">Go to Protected Page</a>
            </body>
        </html>
        """
    else:
        return f"""
        <html>
            <head><title>Temporary Web Service</title></head>
            <body>
                <h1>Welcome to Temporary Web Service</h1>
                <p>You are not logged in.</p>
                <a href="/login">Login with Keycloak</a>
            </body>
        </html>
        """

@app.get("/login")
async def login():
    # Keycloak 로그인 페이지로 리다이렉트
    redirect_uri = "http://test.house.sio2.kr/callback"
    auth_url = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
    params = {
        "client_id": KEYCLOAK_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid profile email"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    login_url = f"{auth_url}?{query_string}"
    
    return RedirectResponse(url=login_url)

@app.get("/callback")
async def callback(code: str):
    # Authorization code를 access token으로 교환
    token_url = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    
    data = {
        "grant_type": "authorization_code",
        "client_id": KEYCLOAK_CLIENT_ID,
        "code": code,
        "redirect_uri": "http://test.house.sio2.kr/callback"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            # 실제 환경에서는 토큰을 쿠키나 세션에 저장
            access_token = token_data.get("access_token")
            
            return f"""
            <html>
                <head><title>Login Success</title></head>
                <body>
                    <h1>Login Successful!</h1>
                    <p>Access Token: {access_token[:50]}...</p>
                    <p>Copy this token and use it in the Authorization header:</p>
                    <code>Authorization: Bearer {access_token}</code>
                    <br><br>
                    <a href="/">Back to Home</a>
                </body>
            </html>
            """
        except Exception as e:
            return f"""
            <html>
                <head><title>Login Error</title></head>
                <body>
                    <h1>Login Failed</h1>
                    <p>Error: {str(e)}</p>
                    <a href="/">Back to Home</a>
                </body>
            </html>
            """

@app.get("/logout")
async def logout():
    # Keycloak 로그아웃 페이지로 리다이렉트
    logout_url = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"
    redirect_uri = "http://test.house.sio2.kr/"
    
    return RedirectResponse(url=f"{logout_url}?redirect_uri={redirect_uri}")

@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return {
        "message": "This is a protected route",
        "user": user,
        "timestamp": "2025-08-13"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "temp-web-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)

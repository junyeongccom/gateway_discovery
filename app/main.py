from fastapi import FastAPI, Request
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI(title="API Gateway")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 환경에서는 특정 도메인으로 제한하는 것이 좋습니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수에서 AUTH 서비스 URL 가져오기, 없으면 기본값 사용
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")

api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {"message": "Welcome to API Gateway"}

# AUTH 서비스로 프록시 요청 라우트
@api_router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(request: Request, path: str):
    url = f"{AUTH_SERVICE_URL}/{path}"
    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body
            )
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code
        )
    except Exception as e:
        return JSONResponse(
            content={"detail": f"Auth service error: {str(e)}"},
            status_code=500
        )

app.include_router(api_router) 
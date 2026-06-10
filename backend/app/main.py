from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        for err in errors:
            loc = err.get("loc", ())
            if "phone" in loc:
                err_type = err.get("type", "")
                if err_type == "string_pattern_mismatch":
                    return JSONResponse(
                        status_code=422,
                        content={"detail": "手机号格式不正确，应为11位有效手机号码"},
                    )
        return JSONResponse(status_code=422, content={"detail": errors[0].get("msg", "请求参数错误")})

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

from fastapi import FastAPI
from admin.presentation.fastapi import router as auth_router, JWTMiddleware

app = FastAPI(
    title="VMS API",
    version="1.0.0",
    description="Sistema de Monitoramento com IA"
)

# Middleware JWT
app.add_middleware(JWTMiddleware)

# Routers
app.include_router(auth_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "vms-api"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .routers import auth, users, styles, wax_batches, molds, stations, inspection_cycles, batches, inspection, dashboard, warnings, delivery_archives, reworks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="手作蜡模试制管理平台 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(styles.router, prefix=settings.API_V1_PREFIX)
app.include_router(wax_batches.router, prefix=settings.API_V1_PREFIX)
app.include_router(molds.router, prefix=settings.API_V1_PREFIX)
app.include_router(stations.router, prefix=settings.API_V1_PREFIX)
app.include_router(inspection_cycles.router, prefix=settings.API_V1_PREFIX)
app.include_router(batches.router, prefix=settings.API_V1_PREFIX)
app.include_router(inspection.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(warnings.router, prefix=settings.API_V1_PREFIX)
app.include_router(delivery_archives.router, prefix=settings.API_V1_PREFIX)
app.include_router(reworks.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {"message": "手作蜡模试制管理平台 API 运行正常"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )

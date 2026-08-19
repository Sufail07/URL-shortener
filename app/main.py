from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import ShortenResponse, ShortenRequest
from .database import get_db, engine, Base
from sqlalchemy import select
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from .models import URL
from .services import URLService
from .config import settings

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.rate_limit_storage)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.shorten_rate_limit)
async def shorten(request: Request, body: ShortenRequest, db: AsyncSession = Depends(get_db)) -> ShortenResponse:
    service = URLService(db)
    try:
        url_entry = await service.create_short_url(body.url)
        return ShortenResponse(id=url_entry.id, short_code=url_entry.short_code, short_url=f"{request.base_url}{url_entry.short_code}", original_url=url_entry.original_url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    
@app.get("/{short_code}")
@limiter.limit(settings.redirect_rate_limit)
async def reroute(request: Request, short_code: str, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    url_entry = result.scalar_one_or_none()
    if not url_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    return RedirectResponse(url=url_entry.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import ShortenResponse, ShortenRequest
from .database import get_db, engine, Base
from sqlalchemy import select
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse
from .models import URL
from .services import URLService

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

@app.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
async def shorten(request: Request, body: ShortenRequest, db: AsyncSession = Depends(get_db)) -> ShortenResponse:
    service = URLService(db)
    try:
        url_entry = await service.create_short_url(body.url)
        return ShortenResponse(id=url_entry.id, short_code=url_entry.short_code, short_url=f"{request.base_url}{url_entry.short_code}", original_url=url_entry.original_url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    
@app.get("/{short_code}")
async def reroute(short_code: str, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    url_entry = result.scalar_one_or_none()
    if not url_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    return RedirectResponse(url=url_entry.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    
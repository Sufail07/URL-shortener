from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
from .models import URL

class URLService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_short_url(self, original_url: str) -> URL:
        for _ in range(5):
            code = secrets.token_urlsafe(6)
            url_entry = URL(original_url=original_url, short_code=code)
            self.db.add(url_entry)
            try:
                await self.db.commit()
                await self.db.refresh(url_entry)
                return url_entry
            except IntegrityError:
                await self.db.rollback()
        raise ValueError("Could not generate a unique short code.")


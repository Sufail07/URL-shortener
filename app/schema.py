from pydantic import BaseModel

class ShortenRequest(BaseModel):
    url: str

class ShortenResponse(BaseModel):
    id: int
    short_code: str
    short_url: str
    original_url: str


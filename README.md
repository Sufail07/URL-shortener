# URL Shortener API

A simple URL shortener built with **FastAPI** and **SQLAlchemy (async)**. Shorten long URLs into compact codes and redirect users with a single GET request.

## Features

- **POST `/shorten`** — accept a long URL, return a short code and the full short URL
- **GET `/{short_code}`** — 307-redirect to the original URL (404 if the code doesn't exist)
- Collision-safe code generation using `secrets.token_urlsafe`
- Async-first stack (asyncpg / aiosqlite + async SQLAlchemy session)
- Swagger UI documentation at `/docs`
- Clean layering: routes → service → models

## Tech Stack

| Layer    | Technology                          |
| -------- | ----------------------------------- |
| API      | FastAPI + Uvicorn                   |
| ORM      | SQLAlchemy 2.x (async)              |
| Database | PostgreSQL (asyncpg), SQLite (aiosqlite) for local dev |
| Config   | pydantic-settings (.env)            |
| Tooling  | uv (package manager)                |

## Project Structure

```
url_shortener/
├── app/
│   ├── config.py     # Loads settings from .env
│   ├── database.py   # Async engine, session factory, get_db dependency
│   ├── models.py     # SQLAlchemy URL model
│   ├── schema.py     # Pydantic request/response schemas
│   ├── services.py   # Business logic (code generation, collision handling)
│   └── main.py       # FastAPI app + endpoints + lifespan/startup
├── .env.example      # Example environment variables
├── pyproject.toml    # Project metadata + dependencies
└── uv.lock           # Locked dependency versions
```

## Getting Started

### Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure the environment

```bash
cp .env.example .env
```

The default uses SQLite so you can run it instantly. To use PostgreSQL instead, set:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/urlshort
```

### 3. Run the server

```bash
uv run uvicorn app.main:app --reload
```

Tables are created automatically on startup via the app lifespan hook (no manual migrations needed for this project).

The API will be available at `http://localhost:8000`.

## Usage

### Shorten a URL

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url/path"}'
```

**Response (201 Created):**

```json
{
  "id": 1,
  "short_code": "Ab3xY9",
  "short_url": "http://localhost:8000/Ab3xY9",
  "original_url": "https://example.com/very/long/url/path"
}
```

### Redirect to the original URL

```bash
curl -L http://localhost:8000/Ab3xY9
```

Or just open `http://localhost:8000/Ab3xY9` in a browser — it redirects to the original URL.

**Response codes:**

- `307` — redirect to the original URL
- `404` — unknown short code
- `409` — could not generate a unique code (rare collision)

### Interactive docs

Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI, or `/redoc` for ReDoc.

## How It Works

1. `POST /shorten` validates the URL with Pydantic (`ShortenRequest`).
2. `URLService` generates a random 6-character code with `secrets.token_urlsafe(6)` and stores it with a `UNIQUE` constraint.
3. On the rare chance of a collision, the insert raises `IntegrityError`, the transaction is rolled back, and a `409` is returned.
4. `GET /{short_code}` looks up the code and returns a `RedirectResponse` (307) to the stored URL.

## Roadmap (possible enhancements)

- Configurable code length / expiry dates
- Click-tracking / analytics
- Custom aliases (`POST /shorten` with a chosen code)
- Rate limiting
- Alembic migrations for schema versioning
- Docker Compose for a one-command stack (API + PostgreSQL)
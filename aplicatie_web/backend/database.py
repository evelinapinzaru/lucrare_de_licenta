from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise RuntimeError(
        "Missing environment variable: DATABASE_URL. Define it in the backend .env like this: "
        "DATABASE_URL=postgresql+psycopg://postgres:<PASS>@localhost:5432/codeflow."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
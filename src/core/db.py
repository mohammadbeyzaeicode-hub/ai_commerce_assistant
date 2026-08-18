from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./app.db"
# بعداً فقط اینو عوض می‌کنیم:
# postgresql://user:password@localhost:5432/dbname

engine = create_engine(
    DATABASE_URL,
    echo=True,      # فعلاً روشن: ببینی SQL چی می‌ره
    future=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

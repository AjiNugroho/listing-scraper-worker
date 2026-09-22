import json
import os
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL) if DATABASE_URL else None


class ScrapeResult(SQLModel, table=True):
    __tablename__ = "scrape_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    requested_max_item: int
    collected: int
    post_urls: str
    status: str
    webhook_endpoint: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def init_db():
    SQLModel.metadata.create_all(engine)


def save_scrape_result(result: dict):
    init_db()
    with Session(engine) as session:
        record = ScrapeResult(
            url=result["url"],
            requested_max_item=result["requested_max_item"],
            collected=result["collected"],
            post_urls=json.dumps(result["posts"]),
            status=result["status"],
            webhook_endpoint=result.get("webhook_endpoint", "no-webhook"),
        )
        session.add(record)
        session.commit()

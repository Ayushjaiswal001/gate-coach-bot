"""Pre-populate syllabus_tracker from content/syllabus.yaml. Idempotent (upsert by row key).

Usage: python -m app.scripts.seed
"""

import asyncio
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SyllabusTracker

SYLLABUS_PATH = Path(__file__).resolve().parents[2] / "content" / "syllabus.yaml"


def load_syllabus(path: Path = SYLLABUS_PATH) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


async def seed(session: AsyncSession, data: dict) -> int:
    count = 0
    for field in ["cse", "ece"]:
        if field not in data:
            continue
        order = 0
        for m in data[field]["months"]:
            for wk in m["weeks"]:
                for sub in wk["sub_topics"]:
                    row = await session.scalar(
                        select(SyllabusTracker).where(
                            SyllabusTracker.field == field.upper(),
                            SyllabusTracker.month == m["month"],
                            SyllabusTracker.week == wk["week"],
                            SyllabusTracker.sub_topic == sub,
                        )
                    )
                    if row is None:
                        row = SyllabusTracker(
                            field=field.upper(),
                            month=m["month"],
                            week=wk["week"],
                            sub_topic=sub,
                        )
                        session.add(row)
                    row.subject = wk["subject"]
                    row.is_high_priority = bool(wk.get("hp", False))
                    row.sort_order = order
                    order += 1
                    count += 1
    await session.commit()
    return count


async def main() -> None:
    from app.db.session import SessionLocal, init_db

    Path("data").mkdir(exist_ok=True)
    await init_db()
    async with SessionLocal() as session:
        n = await seed(session, load_syllabus())
    print(f"Seeded {n} syllabus sub-topics.")


if __name__ == "__main__":
    asyncio.run(main())

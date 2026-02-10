import asyncio
from app.db.database import engine
from sqlalchemy import text


async def check_docs():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT count(*) FROM catwiki_documents"))
        count = result.scalar()
        print(f"Total documents: {count}")

        result = await conn.execute(
            text("SELECT site_id, count(*) FROM catwiki_documents GROUP BY site_id")
        )
        rows = result.fetchall()
        for row in rows:
            print(f"Site ID {row[0]}: {row[1]} documents")


if __name__ == "__main__":
    asyncio.run(check_docs())

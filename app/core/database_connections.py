from databases import Database
from sqlalchemy import Column, MetaData, Table, Integer, String, DateTime, create_engine, func


from app.core import configs as CF



database = Database(CF.DATABASE_URL)
metadata = MetaData()


# create table, please add another table if needed
projects_table = Table(
    "project",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(20), nullable=False),
    Column("pic", String(20), nullable=False),
    Column("container_name", String(63), nullable=False),
    Column("created_date", DateTime, default=func.now()),
)

async def get_db():
    try:
        await database.connect()
        yield database
    finally:
        await database.disconnect()


engine = create_engine(CF.DATABASE_URL)
metadata.create_all(engine)
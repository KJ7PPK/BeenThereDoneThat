from .models import transportations
from databases import Database

async def get_all(db: Database):
    return await db.fetch_all(transportations.select())

async def create(db: Database, **kwargs):
    query = transportations.insert().values(**kwargs)
    record_id = await db.execute(query)
    return {**kwargs, "id": record_id}

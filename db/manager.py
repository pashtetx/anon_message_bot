from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import random



class Manager:
    
    def __init__(self, model):
        self.model = model
    
    def parse_query(self, key: str, value: str):
        attr = getattr(self.model, key.split("__")[0])
        if key.endswith("__not"):
            return attr != value
        else:
            return attr == value
    
    def parse_kwargs(self, **kw):
        return [self.parse_query(k,v) for k,v in kw.items()] 
    
    async def get(self, session: AsyncSession, **kw):
        query = select(self.model).where(*self.parse_kwargs(**kw))
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_or_create(self, session: AsyncSession, **kw):
        query = select(self.model).where(*self.parse_kwargs(**kw))
        result = await session.execute(query)
        scalar = result.scalar_one_or_none()
        if not scalar:
            obj = self.model(**kw)
            await obj.save(session)
            return obj
        return scalar
    
    
    async def filter(self):
        pass
    
    async def first(self):
        pass

    async def all(self):
        pass
        
    async def count(self, session: AsyncSession):
        result = await session.execute(select(func.count()).select_from(self.model))
        return result.scalar()
    
    async def random(self, session: AsyncSession, **kw):
        query = select(self.model).where(*self.parse_kwargs(**kw)).offset(random.randrange(await self.count(session))).fetch(1)
        result = await session.execute(query)
        return result.scalar()
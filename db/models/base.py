from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs
from ..manager import Manager

class Base(DeclarativeBase, AsyncAttrs):
    
    @classmethod
    @property
    def objects(cls):
        return Manager(cls)
    
    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()
        await session.refresh(self)
    
    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()
        await session.flush()
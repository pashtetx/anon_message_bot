from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import logging

async def setup_db(url: str) -> None:
    """ Иницилизация базы данных """
    logging.info("Initializing database...")
    engine = create_async_engine(url)
    logging.info("Create database engine...")
    session = async_sessionmaker(bind=engine)
    return session
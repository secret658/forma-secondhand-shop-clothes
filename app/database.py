import certifi
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

#TiDB Cloud требует TLS-соединение, обычный MySQL локально в докере - нет
#certifi.where() дает путь к пачке доверенных корневых сертификатов,
#этого достаточно чтобы pymysql поверил сертификату TiDB (он от общеизвестного CA)
connect_args = {}
if "tidbcloud.com" in settings.DATABASE_URL:
    connect_args = {"ssl": {"ca": certifi.where()}}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
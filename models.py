from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config


url = URL.create(
    drivername="postgresql",
    username=config("DB_USER"),
    password=config("DB_PASSWORD"),
    host=config("DB_HOST"),
    database=config("DB_NAME"),
    port=config("DB_PORT")
)

engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "ad_user"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    message = Column(String)
    response = Column(String)


Base.metadata.create_all(engine)
import configparser
from sqlalchemy import create_engine, inspect
import models.realtime as RT

config = configparser.ConfigParser()
config.read("./gtfs2series.cfg")

system = config.get("database", "system")
host = config.get("database", "host")
port = config.getint("database", "port")
name = config.get("database", "name")
user = config.get("database", "user")
password = config.get("database", "password")

engine = create_engine(f"{system}://{user}:{password}@{host}:{port}/{name}")
inspector = inspect(engine)

RT.Base.metadata.create_all(engine)

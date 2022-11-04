import sqlalchemy
from config import settings
from databases import Database
from fastapi.templating import Jinja2Templates


db = Database(settings.get_db_dsn())
metadata = sqlalchemy.MetaData()
templates = Jinja2Templates('templates')

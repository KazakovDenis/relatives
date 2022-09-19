import sqlalchemy
from databases import Database
from fastapi.templating import Jinja2Templates

from config import settings


db = Database(settings.get_db_dsn())
metadata = sqlalchemy.MetaData()
templates = Jinja2Templates('templates')

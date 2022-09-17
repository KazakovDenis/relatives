import sqlalchemy
from databases import Database
from fastapi.templating import Jinja2Templates


DB_URL = 'sqlite:///relatives.db'
db = Database(DB_URL)
metadata = sqlalchemy.MetaData()
templates = Jinja2Templates('templates')

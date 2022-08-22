import orm
from databases import Database
from fastapi.templating import Jinja2Templates


db = Database('sqlite:///relatives.db')
models = orm.ModelRegistry(database=db)
templates = Jinja2Templates('templates')

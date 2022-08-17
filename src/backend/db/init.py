import orm
from databases import Database


db = Database('sqlite:///relatives.db')
models = orm.ModelRegistry(database=db)


async def init_db():
    await models.create_all()

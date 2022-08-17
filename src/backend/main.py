from fastapi import FastAPI

from db import db, init_db
from db.models import Person

app = FastAPI()


@app.on_event('startup')
async def database_connect():
    await db.connect()
    await init_db()
    await Person.objects.get_or_create(
        {},
        name='Денис',
        surname='Казаков',
    )


@app.on_event('shutdown')
async def database_disconnect():
    await db.disconnect()


@app.get('/')
async def root():
    return await Person.objects.all()

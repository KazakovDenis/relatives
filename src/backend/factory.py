from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


def create_app() -> FastAPI:
    from apps import api_v1, ui
    from deps import db, templates

    app = FastAPI()
    app.include_router(api_v1.router)
    app.include_router(ui.router)
    app.mount('/static', StaticFiles(directory='static'), name='static')

    @app.on_event('startup')
    async def database_connect():
        await db.connect()

    @app.on_event('shutdown')
    async def database_disconnect():
        await db.disconnect()

    @app.get('/', response_class=HTMLResponse)
    async def root(request: Request):
        ctx = {'request': request}
        return templates.TemplateResponse('index.html', ctx)

    return app

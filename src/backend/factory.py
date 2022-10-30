from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.authentication import AuthenticationMiddleware


def create_app() -> FastAPI:
    from apps import api_v1, ui
    from apps.auth.middleware import AuthBackend
    from deps import db, templates

    middlewares = [
        Middleware(AuthenticationMiddleware, backend=AuthBackend()),
    ]

    app = FastAPI(middleware=middlewares)
    app.include_router(api_v1.router)
    app.include_router(ui.router)
    app.mount('/static', StaticFiles(directory='static'), name='static')

    @app.on_event('startup')
    async def startup():
        await db.connect()

    @app.on_event('shutdown')
    async def shutdown():
        await db.disconnect()

    @app.get('/', response_class=HTMLResponse)
    async def root(request: Request):
        ctx = {'request': request, 'public': True}
        return templates.TemplateResponse('public/index.html', ctx)

    return app

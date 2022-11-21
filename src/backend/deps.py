import gettext

import sqlalchemy
from config import settings
from databases import Database
from fastapi.templating import Jinja2Templates


db = Database(settings.get_db_dsn())
metadata = sqlalchemy.MetaData()
templates = Jinja2Templates(settings.TEMPLATES_DIR, extensions=['jinja2.ext.i18n'])
templates.env.install_gettext_callables(
    gettext=gettext.gettext,
    ngettext=gettext.ngettext,
    npgettext=gettext.npgettext,
    pgettext=gettext.pgettext,
    newstyle=True,
)

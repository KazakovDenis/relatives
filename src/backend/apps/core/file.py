from base64 import b64decode
from datetime import datetime
from pathlib import Path

import aiofiles

from config import settings

from .models import Person, Photo


async def photo_from_b64(raw: str, path: str | Path = Path(settings.UPLOADS_DIR)) -> Path:
    meta, b64 = raw.split(';base64,')
    _, ext = meta.split('/')

    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    name = datetime.now().timestamp()
    location = path / f'{name}.{ext}'

    async with aiofiles.open(location, 'wb') as f:
        await f.write(b64decode(b64))

    return location


async def save_person_photo(person: Person, raw: str) -> Photo:
    directory = Path(settings.UPLOADS_DIR) / f'persons/{person.id}'
    location = await photo_from_b64(raw, directory)
    loc = str(location.relative_to(settings.UPLOADS_DIR))
    return await Photo.objects.create(location=loc, person=person)

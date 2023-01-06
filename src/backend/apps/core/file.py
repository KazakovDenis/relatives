import asyncio
import shutil
from base64 import b64decode
from pathlib import Path
from time import time_ns

import aiofiles

from config import settings

from .models import Person, Photo


def get_new_person_photo_loc(person_id: int, extension: str):
    directory = Path(settings.UPLOADS_DIR) / f'persons/{person_id}'
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{time_ns()}.{extension.lstrip('.')}"


async def person_photo_from_b64(raw: str, person_id: int) -> Path:
    meta, b64 = raw.split(';base64,')
    _, ext = meta.split('/')

    location = get_new_person_photo_loc(person_id, ext)

    async with aiofiles.open(location, 'wb') as f:
        await f.write(b64decode(b64))

    return location


async def save_person_photo(person: Person, raw: str) -> Photo:
    location = await person_photo_from_b64(raw, person.id)
    loc = str(location.relative_to(settings.UPLOADS_DIR))
    return await Photo.objects.create(location=loc, person=person)


def copy_person_photo(photo: Photo, to_person: Person) -> Photo:
    old_loc = Path(settings.UPLOADS_DIR) / photo.location
    new_loc = get_new_person_photo_loc(to_person.id, old_loc.suffix)

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, shutil.copy, old_loc, new_loc)

    rel_loc = new_loc.relative_to(settings.UPLOADS_DIR)
    return Photo(location=str(rel_loc), person=to_person)

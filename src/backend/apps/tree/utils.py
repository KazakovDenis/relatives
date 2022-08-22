from typing import Tuple

import aiofiles
import pydantic
import typesystem
from aiocsv import AsyncDictReader

from .models import Person
from .schemas import PersonSchema


async def load_persons_csv(filename: str) -> Tuple[int, int]:
    """Load person data from a CSV-file."""
    loaded = errors = 0
    async with aiofiles.open(filename) as f:
        async for row in AsyncDictReader(f):
            row['birthdate'] = row['birthdate'] or None
            try:
                person = PersonSchema(**row)
                await Person.objects.create(**person.dict())
                loaded += 1
            except (pydantic.ValidationError, typesystem.ValidationError):
                errors += 1
    return loaded, errors

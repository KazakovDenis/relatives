from typing import Tuple

import aiofiles
import pydantic
import typesystem
from aiocsv import AsyncDictReader
from orm import NoMatch

from .constants import RelationType
from .models import Person
from .schemas import PersonSchema


async def load_persons_csv(filename: str) -> Tuple[int, int]:
    """Load person data from a CSV-file."""
    loaded = errors = 0

    async with aiofiles.open(filename) as f:
        async for row in AsyncDictReader(f):
            row['birthdate'] = row['birthdate'] or None
            try:
                validated = PersonSchema(**row)
                person = await Person.objects.create(**validated.dict())
                loaded += 1
            except (pydantic.ValidationError, typesystem.ValidationError):
                errors += 1
                continue

            for person_id, relation in [
                (row['mother'], RelationType.PARENT),
                (row['father'], RelationType.PARENT),
                (row['spouse'], RelationType.SPOUSE),
                *[
                    (ex_spouse_id, RelationType.EX_SPOUSE)
                    for ex_spouse_id in row['ex_spouse'].split(',')
                ],
                *[
                   (child_id, RelationType.CHILD)
                    for child_id in row['children'].split(',')
                ],

            ]:
                if not person_id:
                    continue
                try:
                    relative = await Person.objects.get(id=int(person_id))
                    await person.add_relative(relation, relative)
                except (ValueError, NoMatch):
                    pass

    return loaded, errors

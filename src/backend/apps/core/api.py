from typing import Optional

from fastapi import APIRouter, HTTPException
from orm import MultipleMatches, NoMatch

from .constants import BACK_RELATIONS, RelationType
from .models import Person, PersonTree, Relation, Tree
from .schemas import PersonSchema, RelationSchema, TreeSchema


router = APIRouter()


@router.get('/tree')
async def tree_list():
    return await Tree.objects.all()


@router.post('/tree')
async def tree_create(tree: TreeSchema):
    tree, created = await Tree.objects.get_or_create(**tree.dict())
    return tree


@router.get('/tree/{tid}')
async def tree_detail(tid: int):
    try:
        return await Tree.objects.get(id=tid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Tree not found')


@router.get('/tree/{tid}/scheme')
async def tree_scheme(tid: int):
    pts = await PersonTree.objects.filter(tree__id=tid).select_related('person').all()
    rels = (
        await Relation.objects
        .exclude(type=RelationType.CHILD)
        .all(person_from__in=[p.person.id for p in pts])
    )
    return {
        'nodes': [pt.person for pt in pts],
        'edges': [rel for rel in rels],
    }


@router.get('/persons')
async def person_list():
    return await Person.objects.all()


@router.post('/persons')
async def person_create(person: PersonSchema):
    return await Person.objects.create(**person.dict())


@router.get('/persons/{pid}')
async def person_detail(pid: int):
    try:
        return await Person.objects.get(id=pid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Person not found')


@router.patch('/persons/{pid}')
async def person_update(pid: int, person: PersonSchema):
    await Person.objects.filter(id=pid).update(**person.dict())
    return {'result': 'ok'}


@router.delete('/persons/{pid}')
async def person_delete(pid: int):
    await Person.objects.filter(id=pid).delete()
    return {'result': 'ok'}


@router.get('/persons/{pid}/relatives')
async def person_relatives(pid: int, relation: Optional[str] = None):
    try:
        person = await Person.objects.get(id=pid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Person not found')
    return await person.get_relatives(relation)


@router.get('/relations')
async def relation_list():
    return await Relation.objects.all()


@router.post('/relations')
async def relation_create(relation: RelationSchema):
    rel = await Relation.objects.create(
        person_from=await Person.objects.get(id=relation.person_from),
        person_to=await Person.objects.get(id=relation.person_to),
        type=relation.relation,
    )
    back_rel = await Relation.objects.create(
       person_from=rel.person_to,
       person_to=rel.person_from,
       type=BACK_RELATIONS[relation.relation],
    )
    return {
        'relation': rel,
        'back_relation': back_rel,
    }


@router.get('/relations/{rid}')
async def relation_detail(rid: int):
    try:
        return await Relation.objects.get(id=rid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Relation not found')


@router.delete('/relations/{rid}')
async def relation_delete(rid: int):
    try:
        rel = await Relation.objects.get(id=rid)
    except (NoMatch, MultipleMatches):
        raise HTTPException(status_code=404, detail='Relation not found')

    await Relation.objects.filter(person_from=rel.person_to, person_to=rel.person_from).delete()
    await rel.delete()
    return {'result': 'ok'}

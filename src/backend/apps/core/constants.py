import enum


class RelationType(enum.Enum):
    PARENT = 'PARENT'
    CHILD = 'CHILD'
    SPOUSE = 'SPOUSE'
    EX_SPOUSE = 'EX_SPOUSE'


BACK_RELATIONS = {
    RelationType.PARENT: RelationType.CHILD,
    RelationType.CHILD: RelationType.PARENT,
    RelationType.SPOUSE: RelationType.SPOUSE,
    RelationType.EX_SPOUSE: RelationType.EX_SPOUSE,
}


class Gender(enum.Enum):
    FEMALE = 'FEMALE'
    MALE = 'MALE'

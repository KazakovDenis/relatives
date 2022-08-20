from .constants import RelationType


def ensure_rel_type(rel_type: RelationType) -> RelationType:
    if isinstance(rel_type, RelationType):
        return rel_type
    if not isinstance(rel_type, str):
        raise ValueError(f'Bad relation type: {rel_type}')
    return RelationType(rel_type)

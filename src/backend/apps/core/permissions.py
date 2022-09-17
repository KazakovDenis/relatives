from typing import Optional

from .models import Tree, UserTree


async def has_tree_perm(user_id: int, tree_id: int) -> Optional[Tree]:
    """Check user has view & edit tree permissions."""
    ut = await UserTree.objects.select_related('tree').get_or_none(user__id=user_id, tree__id=tree_id)
    return ut.tree if ut else None

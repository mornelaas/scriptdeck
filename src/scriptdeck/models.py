from enum import Enum


class ScriptStatus(Enum):
    IDEA = "idea"
    BORRADOR = "borrador"
    LISTO = "listo"
    GRABADO = "grabado"
    PUBLICADO = "publicado"


def can_transition(current: ScriptStatus, new: ScriptStatus) -> bool:
    """Return True if a script can move from `current` to `new`."""
    if current == new:
        return True
    if current == ScriptStatus.PUBLICADO:
        return False
    order = list(ScriptStatus)
    step = order.index(new) - order.index(current)
    return step in (1, -1)

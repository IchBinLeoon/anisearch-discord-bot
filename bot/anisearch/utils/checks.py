import logging
from typing import Dict, Any

log = logging.getLogger(__name__)


def is_adult(data: Dict[str, Any]) -> bool:
    if data.get('isAdult') is True:
        return True
    if data.get('is_adult') is True:
        return True
    if data.get('nsfw') is True:
        return True
    return False

from typing import Any


class BaseService:
    def __init__(self, **kwargs: Any):
        self._deps = kwargs

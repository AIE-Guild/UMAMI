import logging
from typing import Tuple

from django.http import HttpRequest

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AdapterRegistry(type):
    """An adapter subclass registry implemented as a metaclass."""

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if not hasattr(cls, '_registry'):
            cls._registry = {}
        else:
            try:
                key = cls.id
            except AttributeError:
                pass
            else:
                if key in cls._registry:
                    raise ImportError('duplicate adapter ID: {}'.format(key))
                cls._registry[key] = cls

    def adapter(cls, key: str):
        """Map an adapter ID to the class.

        Args:
            key: A client subclass adapter_id attribute.

        Returns: The registered adapter subclass.

        """
        try:
            return cls._registry[key]
        except KeyError:
            return

    @property
    def adapters(cls):
        """The list of adapters.

        Returns: All registered adapter subclasses.

        """
        return [cls._registry[key] for key in cls._registry]

    @property
    def choices(cls):
        return [(adapter.id, adapter.name) for adapter in cls.adapters]


class Adapter(object, metaclass=AdapterRegistry):
    scope = tuple()

    def get_authorization_redirect(self, request: HttpRequest) -> Tuple[str, str]:
        return '', ''

import logging
from typing import Callable, Dict, List, Type
from .base import DomainEvent

logger = logging.getLogger(__name__)

class EventDispatcher:
    """
    Lightweight internal event bus.
    Enables uncoupling of services by emitting domain events.
    """
    _listeners: Dict[Type[DomainEvent], List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_class: Type[DomainEvent], listener: Callable):
        if event_class not in cls._listeners:
            cls._listeners[event_class] = []
        cls._listeners[event_class].append(listener)

    @classmethod
    def dispatch(cls, event: DomainEvent):
        event_class = type(event)
        listeners = cls._listeners.get(event_class, [])
        
        for listener in listeners:
            try:
                # In a real-world scenario, this could be offloaded to Celery
                listener(event)
            except Exception as e:
                logger.error(f"Error handling event {event_class.__name__} in {listener.__name__}: {e}")

# Helper for easy access
dispatch = EventDispatcher.dispatch
subscribe = EventDispatcher.subscribe

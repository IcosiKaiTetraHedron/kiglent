from __future__ import annotations

from collections import defaultdict, deque
from types import FunctionType
from typing import Any, Callable, Iterable

EVENT_HANDLED = True
EVENT_UNHANDLED = None

EVENT_HANDLE_STATE = bool | None

class EventDispatcher:
    _events: defaultdict[str, deque[Callable]]
    _event_dispatcher_handlers: deque[EventDispatcher | EventHandler]
    _class_events: set[str] | None = None
    
    def __init_subclass__(cls):
        cls._class_events = set()
        for parent in cls.__bases__:
            try:
                cls._class_events |= parent._class_events
            except TypeError:
                pass
            except AttributeError:
                pass
        super().__init_subclass__()
    
    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance._events = defaultdict(deque)
        instance._event_dispatcher_handlers = deque()
        if cls._class_events:
            for event in cls._class_events:
                if hasattr(instance, event):
                    func = getattr(instance, event)
                    if getattr(func, 'event_using', True):
                        instance._events[event].appendleft(func)
        return instance
    
    @classmethod
    def register_event_type(cls, event: str) -> None:
        try:
            cls._class_events.add(event)
        except AttributeError:
            cls._class_events = {event}
    
    def add_event(self, event: str, func: Callable) -> None:
        self._events[event].appendleft(func)
    
    def extend_event(self, event: str, func: Iterable[Callable]) -> None:
        self._events[event].extendleft(func)
    
    def event(self, func: FunctionType) -> FunctionType:
        self.add_event(func.__name__, func)
        return func
    
    def push_handler(self, handler: EventHandler | EventDispatcher) -> None:
        self._event_dispatcher_handlers.appendleft(handler)
    
    def remove_handler(self, handler: EventHandler | EventDispatcher) -> None:
        self._event_dispatcher_handlers.remove(handler)
    
    def update_events(self, **functions: Callable) -> None:
        for event, func in functions.items():
            self.add_event(event, func)
    
    def pop_event(self, event: str) -> Callable:
        return self._events.get(event).popleft()
    
    def remove_event(self, event: str, func: Callable) -> None:
        self._events[event].remove(func)
    
    def has_event(self, event: str) -> bool:
        if self._events:
            return event in self._events
        return False 
    
    def get_events(self) -> set[str]:
        if self._events:
            return set(self._events.keys())
        return set()
    
    def dispatch_event(self, event: str, *args, **kwargs) -> bool:
        functions = self._events.get(event)
        if functions:
            for func in functions:
                if func(*args, **kwargs):
                    return True
        
        if self._event_dispatcher_handlers:
            for handler in self._event_dispatcher_handlers:
                if handler.dispatch_event(event, *args, **kwargs):
                    return True
        
        return False
    
    def to_dispatch_event(self, event: str) -> Callable:
        def func(*args, **kwargs):
            return self.dispatch_event(event, *args, **kwargs)
        func.__name__ = event
        return func


class EventHandler:
    def dispatch_event(self, event: str, *args, **kwargs) -> None | bool:
        return getattr(self, event)(*args, **kwargs)
    
    def to_dispatch_event(self, event: str) -> Callable:
        return getattr(self, event)


def event_typing(func: FunctionType) -> FunctionType:
    func.event_using = False
    return func


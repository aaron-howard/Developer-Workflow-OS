from typing import Callable, List, Dict
from ..adapters.base import AgenticEvent

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[AgenticEvent], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[AgenticEvent], None]):
        """Subscribe to a specific event type, or '*' for all events."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event: AgenticEvent):
        """Publish an event to all relevant subscribers."""
        # Exact match subscribers
        for callback in self.subscribers.get(event.type, []):
            callback(event)
            
        # Wildcard subscribers
        for callback in self.subscribers.get("*", []):
            callback(event)

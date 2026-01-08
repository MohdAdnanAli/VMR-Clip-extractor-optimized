"""Event bus for real-time communication between monitoring components."""
import threading
from typing import Dict, List, Callable, Any
from collections import defaultdict
import logging


class EventBus:
    """Central message broker for real-time communication between components."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish an event to all subscribers."""
        with self._lock:
            subscribers = self._subscribers.get(event_type, [])
            
        for handler in subscribers:
            try:
                handler(event_type, data)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event_type}: {e}")
    
    def subscribe(self, event_type: str, handler: Callable[[str, Dict], None]) -> None:
        """Subscribe to events of a specific type."""
        with self._lock:
            self._subscribers[event_type].append(handler)
            self.logger.debug(f"Subscribed handler to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable[[str, Dict], None]) -> None:
        """Unsubscribe from events of a specific type."""
        with self._lock:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                self.logger.debug(f"Unsubscribed handler from {event_type}")
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        with self._lock:
            return len(self._subscribers.get(event_type, []))
    
    def clear_subscribers(self, event_type: str = None) -> None:
        """Clear all subscribers for an event type, or all if None."""
        with self._lock:
            if event_type:
                self._subscribers[event_type].clear()
            else:
                self._subscribers.clear()


# Global event bus instance
event_bus = EventBus()
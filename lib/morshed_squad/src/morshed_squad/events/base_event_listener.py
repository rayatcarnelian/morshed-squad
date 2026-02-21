"""Base event listener for Morshed Squad event system."""

from abc import ABC, abstractmethod

from morshed_squad.events.event_bus import MorshedSquadEventsBus, crewai_event_bus


class BaseEventListener(ABC):
    """Abstract base class for event listeners."""

    verbose: bool = False

    def __init__(self) -> None:
        """Initialize the event listener and register handlers."""
        super().__init__()
        self.setup_listeners(crewai_event_bus)
        crewai_event_bus.validate_dependencies()

    @abstractmethod
    def setup_listeners(self, crewai_event_bus: MorshedSquadEventsBus) -> None:
        """Setup event listeners on the event bus.

        Args:
            crewai_event_bus: The event bus to register listeners on.
        """
        pass

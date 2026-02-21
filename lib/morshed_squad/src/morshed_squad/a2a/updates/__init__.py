"""A2A update mechanism configuration types."""

from morshed_squad.a2a.updates.base import (
    BaseHandlerKwargs,
    PollingHandlerKwargs,
    PushNotificationHandlerKwargs,
    PushNotificationResultStore,
    StreamingHandlerKwargs,
    UpdateHandler,
)
from morshed_squad.a2a.updates.polling.config import PollingConfig
from morshed_squad.a2a.updates.polling.handler import PollingHandler
from morshed_squad.a2a.updates.push_notifications.config import PushNotificationConfig
from morshed_squad.a2a.updates.push_notifications.handler import PushNotificationHandler
from morshed_squad.a2a.updates.streaming.config import StreamingConfig
from morshed_squad.a2a.updates.streaming.handler import StreamingHandler


UpdateConfig = PollingConfig | StreamingConfig | PushNotificationConfig

__all__ = [
    "BaseHandlerKwargs",
    "PollingConfig",
    "PollingHandler",
    "PollingHandlerKwargs",
    "PushNotificationConfig",
    "PushNotificationHandler",
    "PushNotificationHandlerKwargs",
    "PushNotificationResultStore",
    "StreamingConfig",
    "StreamingHandler",
    "StreamingHandlerKwargs",
    "UpdateConfig",
    "UpdateHandler",
]

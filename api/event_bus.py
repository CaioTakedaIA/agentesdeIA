import asyncio
import json
import logging
from typing import Any, AsyncGenerator

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._listeners: set[asyncio.Queue] = set()

    async def listen(self) -> AsyncGenerator[str, None]:
        q = asyncio.Queue()
        self._listeners.add(q)
        try:
            while True:
                msg = await q.get()
                yield f"data: {msg}\n\n"
        except asyncio.CancelledError:
            self._listeners.remove(q)
            raise

    def publish(self, event_type: str, data: Any):
        msg = json.dumps({"type": event_type, "data": data})
        for q in self._listeners:
            try:
                q.put_nowait(msg)
            except Exception as e:
                logger.error("Error publishing to queue: %s", e)


event_bus = EventBus()

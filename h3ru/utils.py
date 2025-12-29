import asyncio
import os
from typing import List
from fastapi import WebSocket

# Shared mutable state
RESULT_MESSAGE: str = ""
lock = asyncio.Lock()

# Simple user/password store (move to secure store later)
USER_PASSWORDS = {"user1": "1234", "user2": "5678"}

# Active websocket lists
active_connections: List[WebSocket] = []
voice_connections: List[WebSocket] = []

# sound directory will be set relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SOUNDS_DIR = os.path.join(PROJECT_ROOT, 'static', 'sounds')


async def broadcast_message(message: str):
    """Placeholder; this is replaced by ws.broadcast_message when router imported."""
    # This function is re-bound by ws router during import-time to close circular imports.
    raise NotImplementedError('broadcast_message not initialized')

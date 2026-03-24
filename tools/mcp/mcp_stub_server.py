"""
Minimal MCP stub server for local development and CI.

Purpose:
 - Accept websocket connections on ws://127.0.0.1:8080 (override via env MCP_HOST/MCP_PORT).
 - Responds "ok" to ping handshakes.
 - Responds "error" to action requests so clients fall back to POM logic while keeping the MCP
   transport healthy for connectivity checks.

This keeps MCP-tagged tests connected without taking over Playwright interactions.
"""

import asyncio
import json
import os
import signal
from typing import Any, Dict

import websockets


async def handle_message(message: str) -> Dict[str, Any]:
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        return {"status": "error", "error": "invalid json"}

    action = data.get("action")

    if action == "ping":
        return {"status": "ok", "pong": True}

    # For all other actions, signal error so client uses its POM fallback.
    return {
        "status": "error",
        "error": f"stub server does not execute '{action}', please use POM fallback",
    }


async def handler(websocket):
    async for message in websocket:
        response = await handle_message(message)
        await websocket.send(json.dumps(response))


async def main():
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8080"))

    stop = asyncio.Future()

    loop = asyncio.get_running_loop()
    for signame in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signame, stop.set_result, None)
        except NotImplementedError:
            # Windows may not support add_signal_handler for SIGTERM.
            pass

    async with websockets.serve(
        handler,
        host,
        port,
        ping_interval=20,
        ping_timeout=10,
        max_queue=32,
    ):
        print(f"[MCP stub] Listening on ws://{host}:{port}")
        await stop


if __name__ == "__main__":
    asyncio.run(main())

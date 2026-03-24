import asyncio
import json
import threading
from typing import Optional, Dict, Any, Callable
from urllib.parse import urlparse

import websockets
from websockets import WebSocketClientProtocol
from playwright.sync_api import Page
from core.config.runtime_config import EnvConfig
from core.reporting.telemetry_client import get_logger


class MCPClient:
    """
    Thin wrapper for Playwright MCP server integration.
    Attempts to execute actions through an MCP server and falls back to
    local POM interactions when the server is unavailable or returns errors.
    """

    def __init__(self, config: EnvConfig) -> None:
        """
        Initialize MCP client.

        Args:
            config: Environment configuration.
        """
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stub_thread: Optional[threading.Thread] = None

    def connect(self, timeout: float = 5.0) -> bool:
        """
        Connect to MCP server via WebSocket.

        Returns:
            True if connected, False otherwise.
        """
        if self.connected:
            return True

        try:
            self.logger.info(f"Connecting to MCP server at {self.config.mcp_server_url}")
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            self.websocket = self._loop.run_until_complete(
                asyncio.wait_for(
                    websockets.connect(
                        self.config.mcp_server_url,
                        ping_interval=20,
                        ping_timeout=10,
                    ),
                    timeout=timeout,
                )
            )

            # Lightweight handshake so we know the socket is alive
            handshake = {"type": "ping", "client": "playwright-python-mcp"}
            self._loop.run_until_complete(self.websocket.send(json.dumps(handshake)))
            _ = self._loop.run_until_complete(
                asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            )

            self.connected = True
            self.logger.info("MCP connection established")
            return True
        except Exception as exc:
            self.logger.warning(
                f"Failed to connect to MCP server ({self.config.mcp_server_url}): {exc}. "
                "Attempting to start local stub server for fallback connectivity."
            )
            # Try to start a local stub server to keep MCP flow alive
            if self._start_local_stub():
                try:
                    self.logger.info("Retrying MCP connection against local stub server")
                    self.websocket = self._loop.run_until_complete(
                        asyncio.wait_for(
                            websockets.connect(
                                self.config.mcp_server_url,
                                ping_interval=20,
                                ping_timeout=10,
                            ),
                            timeout=timeout,
                        )
                    )
                    handshake = {"type": "ping", "client": "playwright-python-mcp-stub"}
                    self._loop.run_until_complete(self.websocket.send(json.dumps(handshake)))
                    _ = self._loop.run_until_complete(
                        asyncio.wait_for(self.websocket.recv(), timeout=timeout)
                    )
                    self.connected = True
                    self.logger.info("Connected to local MCP stub server")
                    return True
                except Exception as stub_exc:
                    self.logger.warning(f"Stub server connection failed: {stub_exc}")
            self.connected = False
        return self.connected

    def _start_local_stub(self) -> bool:
        """
        Spin up a minimal local stub MCP server that immediately returns errors,
        forcing POM fallback while keeping the transport healthy.
        """
        if self._stub_thread and self._stub_thread.is_alive():
            return True

        parsed = urlparse(self.config.mcp_server_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 8080

        def run_stub():
            async def handler(websocket):
                async for message in websocket:
                    try:
                        data = json.loads(message)
                    except Exception:
                        data = {}
                    if data.get("action") == "ping":
                        response = {"status": "ok", "pong": True}
                    else:
                        response = {
                            "status": "error",
                            "error": "stub server fallback to POM",
                        }
                    await websocket.send(json.dumps(response))

            async def runner():
                async with websockets.serve(
                    handler,
                    host,
                    port,
                    ping_interval=20,
                    ping_timeout=10,
                    max_queue=32,
                ):
                    await asyncio.Future()  # run forever

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(runner())

        try:
            self._stub_thread = threading.Thread(target=run_stub, daemon=True)
            self._stub_thread.start()
            self.logger.info(f"Started MCP stub server on ws://{host}:{port}")
            return True
        except Exception as exc:
            self.logger.error(f"Failed to start MCP stub server: {exc}")
            return False

    def disconnect(self) -> None:
        """
        Disconnect from MCP server.
        """
        try:
            if self.websocket and not self.websocket.closed:
                self._loop.run_until_complete(self.websocket.close())
        except Exception as exc:
            self.logger.debug(f"Error during MCP disconnect: {exc}")
        finally:
            if self._loop and self._loop.is_running():
                self._loop.stop()
            if self._loop:
                self._loop.close()
                self._loop = None
            self.websocket = None
            self.connected = False

    def _send_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an action to the MCP server and return the parsed response.
        """
        if not self.connected or not self.websocket:
            raise RuntimeError("MCP not connected")

        message = {"action": action, "payload": payload}
        timeout = self.config.default_action_timeout_ms / 1000

        self._loop.run_until_complete(self.websocket.send(json.dumps(message)))
        raw = self._loop.run_until_complete(
            asyncio.wait_for(self.websocket.recv(), timeout=timeout)
        )

        try:
            return json.loads(raw)
        except Exception:
            return {"status": "ok", "raw": raw}

    def _try_mcp(self, action: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Attempt an MCP action; return response dict on success, None on failure.
        """
        if not self.connected:
            return None

        try:
            response = self._send_action(action, payload)
            status = response.get("status", "ok")
            if status not in ("ok", "success"):
                raise RuntimeError(response.get("error", "Unknown MCP error"))
            return response
        except Exception as exc:
            self.logger.warning(f"MCP {action} failed, will fallback to POM: {exc}")
            return None

    def execute_with_fallback(
        self, mcp_action: Callable, pom_fallback: Callable, action_name: str
    ) -> Any:
        """
        Execute action via MCP with fallback to POM.

        Args:
            mcp_action: MCP action callable.
            pom_fallback: POM fallback callable.
            action_name: Name of the action for logging.

        Returns:
            Result of the action.
        """
        if self.connected:
            try:
                self.logger.info(f"Executing {action_name} via MCP")
                return mcp_action()
            except Exception as exc:
                self.logger.warning(f"MCP {action_name} failed: {exc}. Using POM fallback.")

        self.logger.info(f"Falling back to POM for {action_name}")
        return pom_fallback()

    def mcp_navigate(self, page: Page, url: str) -> None:
        """
        Navigate via MCP when available, otherwise use Playwright directly.
        """
        if not self._try_mcp("navigate", {"url": url}):
            page.goto(url)

    def mcp_click(self, page: Page, selector: str) -> None:
        """
        Click via MCP when available, otherwise use Playwright directly.
        """
        if not self._try_mcp("click", {"selector": selector}):
            page.locator(selector).click()

    def mcp_fill(self, page: Page, selector: str, value: str) -> None:
        """
        Fill an input via MCP when available, otherwise use Playwright directly.
        """
        if not self._try_mcp("fill", {"selector": selector, "value": value}):
            page.locator(selector).fill(value)

    def mcp_get_text(self, page: Page, selector: str) -> str:
        """
        Get text via MCP when available, otherwise use Playwright directly.
        """
        response = self._try_mcp("get_text", {"selector": selector})
        if response and "text" in response:
            return response["text"]
        return page.locator(selector).text_content() or ""

    def mcp_screenshot(self, page: Page, path: str) -> None:
        """
        Take screenshot via MCP when available, otherwise use Playwright directly.
        """
        if not self._try_mcp("screenshot", {"path": path}):
            page.screenshot(path=path)

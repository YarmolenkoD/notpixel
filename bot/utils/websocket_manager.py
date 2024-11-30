import asyncio
from io import BytesIO

from PIL import Image
from aiohttp import WSMsgType, ClientSession, ClientConnectionError

from bot.utils import centrifuge, logger


class WebsocketError(Exception):
    """Custom exception for WebSocket errors."""
    pass


class WebSocketClosedError(WebsocketError):
    pass


class WebSocketGeneralError(WebsocketError):
    pass


class WebSocketUnhandledError(WebsocketError):
    pass


class WebsocketManager:
    def __init__(self, http_client: ClientSession, token: str):
        self.websocket = None
        self.payload = None
        self.websocket_url = "wss://notpx.app/connection/websocket"
        self.http_client = http_client
        self.token = token

    async def __generate_payload(self, token):
        auth_data = f'{{"token":"{token}"}}'

        auth_command = [
            {
                "connect": {
                    "data": auth_data.encode(),
                    "name": "js",
                },
                "id": 1,
            }
        ]
        return centrifuge.encode_commands(auth_command)

    async def __get_data(self):
        msg = await self.websocket.receive()
        if msg.type == WSMsgType.BINARY:
            decoded_data = centrifuge.decode_message(msg.data)
            if isinstance(decoded_data, bytes):
                image = Image.open(BytesIO(decoded_data))
                return image
            elif msg.type == WSMsgType.TEXT:
                return decoded_data
            elif msg.type == WSMsgType.CLOSE:
                raise WebSocketClosedError(f"WebSocket closed with code: {decoded_data}")
            elif msg.type == WSMsgType.ERROR:
                raise WebSocketGeneralError(f"WebSocket error: {decoded_data}")
            else:
                raise WebSocketUnhandledError(f"Unhandled WebSocket message type: {msg.type}")

    async def get_canvas(self):
        try:
            self.websocket = await self.http_client.ws_connect(
                url=self.websocket_url,
                protocols=["centrifuge-protobuf"],
            )
            self.payload = await self.__generate_payload(self.token)
            await self.websocket.send_bytes(self.payload)

            base_delay = 2
            max_retries = 5

            for attempt in range(max_retries):
                try:
                    data = await self.__get_data()
                    if isinstance(data, str):
                        logger.error(f"Received text response: {data}")
                        continue
                    elif isinstance(data, Image.Image):
                        #logger.info("Canvas received")
                        return data
                except WebSocketClosedError as e:
                    logger.error(f"WebSocket closed error: {e}")
                except WebSocketGeneralError as e:
                    logger.error(f"WebSocket general error: {e}")
                except WebSocketUnhandledError as e:
                    logger.error(f"Unhandled WebSocket error: {e}")

                delay = base_delay * (attempt + 1)
                logger.warning(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

            logger.error("Max retries reached, failed to get Canvas data")
        except ClientConnectionError as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            await self.close_websocket()

    async def close_websocket(self):
        if self.websocket:
            await self.websocket.close()

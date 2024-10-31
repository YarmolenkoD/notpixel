# import asyncio
# import logging
# import signal
#
# from centrifuge import (
#     CentrifugeError,
#     Client,
#     ClientEventHandler,
#     ConnectedContext,
#     ConnectingContext,
#     DisconnectedContext,
#     ErrorContext,
#     JoinContext,
#     LeaveContext,
#     PublicationContext,
#     SubscribedContext,
#     SubscribingContext,
#     SubscriptionErrorContext,
#     UnsubscribedContext,
#     SubscriptionEventHandler,
#     ServerSubscribedContext,
#     ServerSubscribingContext,
#     ServerUnsubscribedContext,
#     ServerPublicationContext,
#     ServerJoinContext,
#     ServerLeaveContext,
# )
#
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
# # )
#
# # cf_logger = logging.getLogger("centrifuge")
# # cf_logger.setLevel(logging.DEBUG)
#
# class ClientEventLoggerHandler(ClientEventHandler):
#     """Check out comments of ClientEventHandler methods to see when they are called."""
#
#     async def on_connecting(self, ctx: ConnectingContext) -> None:
#         logging.info("connecting: %s", ctx)
#
#     async def on_connected(self, ctx: ConnectedContext) -> None:
#         logging.info("connected: %s", ctx)
#
#     async def on_disconnected(self, ctx: DisconnectedContext) -> None:
#         logging.info("disconnected: %s", ctx)
#
#     async def on_error(self, ctx: ErrorContext) -> None:
#         logging.error("client error: %s", ctx)
#
#     async def on_subscribed(self, ctx: ServerSubscribedContext) -> None:
#         logging.info("subscribed server-side sub: %s", ctx)
#
#     async def on_subscribing(self, ctx: ServerSubscribingContext) -> None:
#         logging.info("subscribing server-side sub: %s", ctx)
#
#     async def on_unsubscribed(self, ctx: ServerUnsubscribedContext) -> None:
#         logging.info("unsubscribed from server-side sub: %s", ctx)
#
#     async def on_publication(self, ctx: ServerPublicationContext) -> None:
#         logging.info("publication from server-side sub: %s", ctx.pub.data)
#
#     async def on_join(self, ctx: ServerJoinContext) -> None:
#         logging.info("join in server-side sub: %s", ctx)
#
#     async def on_leave(self, ctx: ServerLeaveContext) -> None:
#         logging.info("leave in server-side sub: %s", ctx)
#
# class SubscriptionEventLoggerHandler(SubscriptionEventHandler):
#     async def on_subscribing(self, ctx: SubscribingContext) -> None:
#         logging.info("subscribing: %s", ctx)
#
#     async def on_subscribed(self, ctx: SubscribedContext) -> None:
#         logging.info("subscribed: %s", ctx)
#
#     async def on_unsubscribed(self, ctx: UnsubscribedContext) -> None:
#         logging.info("unsubscribed: %s", ctx)
#
#     async def on_publication(self, ctx: PublicationContext) -> None:
#         logging.info("publication: %s", ctx.pub.data)
#
#     async def on_join(self, ctx: JoinContext) -> None:
#         logging.info("join: %s", ctx)
#
#     async def on_leave(self, ctx: LeaveContext) -> None:
#         logging.info("leave: %s", ctx)
#
#     async def on_error(self, ctx: SubscriptionErrorContext) -> None:
#         logging.error("subscription error: %s", ctx)
#



#     def generate_sec_websocket_key(self):
#         # Генерируем 16 случайных байтов
#         random_bytes = os.urandom(16)
#         # Кодируем в формат Base64
#         sec_websocket_key = base64.b64encode(random_bytes).decode('utf-8')
#         return sec_websocket_key
#     async def send_null_bytes(self):
#         # Цикл отправки нулевых байт с интервалом
#         while True:
#             try:
#                 # Отправляем бинарные данные с нулевыми байтами
#                 await self.socket.send_bytes(b'\x00')
#                 print("Отправлены нулевые байты")
#             except Exception as e:
#                 print(f"Ошибка при отправке нулевых байт: {e}")
#                 break
#             # Ждем 10 секунд перед следующей отправкой (можно настроить интервал)
#             await asyncio.sleep(10)

#     async def get_client_token(self, http_client: aiohttp.ClientSession):
#         curr_user = await self.get_user_info(http_client=http_client, show_error_message=False)
#         ws_token = curr_user.get('websocketToken', None)
#         return ws_token

#     async def create_socket_connection(self, http_client: aiohttp.ClientSession):
#         async def get_client_token():
#             curr_user = await self.get_user_info(http_client=http_client, show_error_message=False)
#             ws_token = curr_user.get('websocketToken', None)
#             return ws_token
#
#         curr_token = await get_client_token()
#         client = Client(
#             "wss://notpx.app/connection/websocket",
#             events=ClientEventLoggerHandler(),
#             token=curr_token,
#             get_token=get_client_token,
#             use_protobuf=True,
#         )
#
#         sub = client.new_subscription(
#             "pixel:message",
#             token=curr_token,
#             get_token=get_client_token,
#         )
#
#         try:
#             await client.connect()
#             self.info("Connected to WebSocket.")
#         except CentrifugeError as e:
#             self.error(f"Connection error: {e}")
#             return
#
#         try:
#             await sub.subscribe()
#             self.info("Subscribed to channel.")
#         except CentrifugeError as e:
#             self.error(f"Subscription error: {e}")
#             return
#
#         return None

#     async def create_socket_connection(self, http_client: aiohttp.ClientSession):
#         uri = "wss://notpx.app/api/v2/image/ws"
#
#         curr_user = await self.get_user_info(http_client=http_client, show_error_message=False)
#
#         user_id = curr_user.get('id', None)
#         ws_token = curr_user.get('websocketToken', None)
#
#         headers_socket['User-Agent'] = http_client.headers['User-Agent']
#         headers_socket['Authorization'] = http_client.headers['Authorization']
#         headers_socket['Sec-Websocket-Key'] = self.generate_sec_websocket_key()
#
#         try:
#             socket = await http_client.ws_connect(uri, headers=headers_socket)
#
#             self.socket = socket
#
#             self.success("WebSocket connected successfully")
#
#             return socket
#
#         except Exception as e:
#             self.warning(f"WebSocket connection error: {e}")
#             return None

# async def draw_template_socket(self, http_client: aiohttp.ClientSession, template_info):
#         try:
#             if not template_info:
#                 return None
#
#             curr_template_id = template_info.get('id', 'Durov')
#             curr_image = template_info.get('image', None)
#             curr_start_x = template_info.get('x', 0)
#             curr_start_y = template_info.get('y', 0)
#             curr_image_size = template_info.get('image_size', 128)
#
#             if not curr_image:
#                 return None
#
#             status_data = await self.get_status(http_client=http_client)
#
#             if status_data == None:
#                 return None
#
#             if not self.socket:
#                 return None
#
#             charges = status_data['charges']
#
#             self.current_user_balance = status_data['userBalance']
#
#             if charges > 0:
#                 self.info(f"Energy: <cyan>{charges}</cyan> ⚡️")
#             else:
#                 self.info(f"No energy ⚡️")
#                 return None
#
#             subscribe_message = json.dumps({
#                 "action": "subscribe",
#                 "channel": "pixel:message"
#             })
#
#             await self.socket.send_str(subscribe_message)
#
#             socket_error = False
#
#             tries = 2
#
#             while charges > 0:
#                 try:
#                     break_socket = False
#
#                     message = await asyncio.wait_for(self.socket.receive(), timeout=random.choices([8.0, 9.0, 10.0, 11.0], weights=[25, 25, 25, 25])[0])
#
#                     if message.type == aiohttp.WSMsgType.CLOSE:
#                         break
#                     elif message.type == aiohttp.WSMsgType.TEXT:
#                         updates = message.data.split("\n")
#                         for update in updates:
#                             match = re.match(r'pixelUpdate:(\d+):#([0-9A-Fa-f]{6})', update)
#
#                             if match:
#                                 pixel_index = match.group(1)
#
#                                 if len(pixel_index) < 6:
#                                     continue
#
#                                 updated_y = int(str(pixel_index)[:3])
#                                 updated_x = int(str(pixel_index)[3:]) - 1
#                                 updated_pixel_color = f"#{match.group(2)}"
#
#                                 if updated_x > curr_start_x and updated_x < curr_start_x + curr_image_size and updated_y > curr_start_y and updated_y < curr_start_y + curr_image_size:
#                                     image_pixel = curr_image.getpixel((updated_x - curr_start_x, updated_y - curr_start_y))
#                                     image_hex_color = '#{:02x}{:02x}{:02x}'.format(*image_pixel)
#
#                                     if image_hex_color.upper() != updated_pixel_color.upper():
#                                         charges = charges - 1
#                                         pixelId = int(f'{updated_x}{updated_y}')+1
#                                         await self.send_draw_request(http_client=http_client, update=(pixelId, updated_x, updated_y, image_hex_color.upper()), template_id=curr_template_id)
#                                         break
#                 except Exception as e:
#                     if self.check_timeout_error(e) or self.check_error(e, "Service Unavailable"):
#                         status_data = await self.get_status(http_client=http_client, show_error_message=False)
#
#                         if status_data:
#                             charges = status_data['charges']
#                             self.current_user_balance = status_data['userBalance']
#
#                         if tries > 0 and charges > 0:
#                             self.warning(f"Warning during painting <cyan>[{self.mode}]</cyan>: <magenta>Notpixel</magenta> server is not response. Retrying..")
#                             tries = tries - 1
#                             sleep_time = random.randint(10, 20)
#                             self.info(f"Restart drawing in {round(sleep_time)} seconds...")
#                             await asyncio.sleep(delay=sleep_time)
#                             continue
#                         else:
#                             self.warning(f"Warning during painting <cyan>[{self.mode}]</cyan>: <magenta>Notpixel</magenta> server is not response. Go to sleep..")
#                             break
#                     elif self.check_error(e, "Bad Request"):
#                         self.warning(f"Warning during painting <cyan>[{self.mode}]</cyan>: <light-yellow>Bad Request</light-yellow>. Go to sleep..")
#                         break
#                     else:
#                         self.error(f"Unknown error during painting <cyan>[{self.mode}]</cyan>: {e}")
#                         break
#         except Exception as error:
#             if self.check_timeout_error(error) or self.check_error(error, "Service Unavailable"):
#                 self.warning(f"Warning during painting <cyan>[{self.mode}]</cyan>: <magenta>Notpixel</magenta> server is not response. Go to sleep..")
#             elif self.check_error(error, "Bad Request"):
#                 self.warning(f"Warning during painting <cyan>[{self.mode}]</cyan>: <light-yellow>Bad Request</light-yellow>. Go to sleep..")
#             else:
#                 if error:
#                     self.error(f"Unknown error during painting <cyan>[{self.mode}]</cyan>: <light-yellow>{error}</light-yellow>")
#                 else:
#                     self.error(f"Unknown error during painting <cyan>[{self.mode}]</cyan>.")
#             await asyncio.sleep(delay=random.randint(2, 5))

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

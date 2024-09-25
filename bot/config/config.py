from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    USE_REF: bool = True
    REF_ID: str = 'f355876562'

    USE_RANDOM_DELAY_IN_RUN: bool = True
    RANDOM_DELAY_IN_RUN: list[int] = [5, 60]

    SLEEP_TIME_IN_MINUTES: list[int] = [120, 180]

    ENABLE_AUTO_TASKS: bool = False
    ENABLE_AUTO_DRAW: bool = True
    ENABLE_JOIN_TG_CHANNELS: bool = False
    ENABLE_CLAIM_REWARD: bool = True
    ENABLE_AUTO_UPGRADE: bool = True

    BOOSTS_BLACK_LIST: list[str] = ['INVITE_FRIENDS', 'TON_TRANSACTION', 'BOOST_CHANNEL', 'ACTIVITY_CHALLENGE', 'CONNECT_WALLET']
    TASKS_TODO_LIST: list[str] = ["x:notcoin", "x:notpixel", "paint20pixels", "leagueBonusSilver", "invite3frens", "leagueBonusGold"]

    USE_PROXY_FROM_FILE: bool = True


settings = Settings()



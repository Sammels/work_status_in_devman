import time
import logging
import logging.handlers
import requests
import telegram

from pathlib import Path

from textwrap import dedent
from retry import retry
from environs import Env

logger = logging.getLogger(__file__)


class BotHandler(logging.Handler):
    def __init__(self, tg_bot_logger_token, tg_chat_id):
        super().__init__()
        self.tg_bot_logger_token = tg_bot_logger_token
        self.tg_chat_id = tg_chat_id

    def emit(self, record):
        bot = telegram.Bot(token=self.tg_bot_logger_token)
        log_entry = self.format(record)
        bot.send_message(
            chat_id=self.tg_chat_id,
            text=rf"{log_entry}",
        )


def get_reviews(token):
    """
    :param token: str
    :return: json
    """
    url = "https://dvmn.org/api/long_polling/"

    header = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=header, timeout=20)
    response.raise_for_status()
    return response.json()


@retry(requests.exceptions.ConnectionError, delay=30)
def check_reviews(token, params, bot, tg_chat_id, logger):
    """

    :param token: str Token for connect to devman api
    :param params: dict empty
    :param bot: Token for connect to Telegram
    :param tg_chat_id: Personal id for chatting with bot.
    :return:
    """
    last_timestamp = None
    while True:
        try:
            reviews = get_reviews(token)
        except requests.exceptions.ReadTimeout:
            continue

        if reviews["status"] == "timeout":
            server_timestamp = reviews["timestamp_to_request"]
            params = {
                "timestamp": int(server_timestamp),
            }
        else:
            current_review = reviews["new_attempts"][0]
            params = {
                "timestamp": current_review["timestamp"],
            }
            new_timestamp = current_review["timestamp"]
            if new_timestamp is last_timestamp:
                continue
            if current_review["is_negative"]:
                bot.send_message(
                    chat_id=tg_chat_id,
                    text=dedent(
                        f"""
                        Преподаватель проверил работу! {current_review['lesson_title']},
                        Есть ошибки.
                        Ссылка на работу {current_review['lesson_url']}
                        """
                    ),
                )
            else:
                bot.send_message(
                    chat_id=tg_chat_id,
                    text=dedent(
                        f"""
                        Преподаватель проверил работу {current_review["lesson_title"]},
                        Всё в порядке.
                        """
                    ),
                )
            last_timestamp = new_timestamp


def config_logger(tg_bot_logger_token, tg_chat_id, logger):
    BASE_DIR = Path(__file__).resolve().parent

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s",
    )
    rotating_file_handler = logging.handlers.RotatingFileHandler(
        f"{BASE_DIR}/botlog.txt", mode="w", maxBytes=200, backupCount=2
    )

    logger.addHandler(rotating_file_handler)
    logger.addHandler(BotHandler(tg_bot_logger_token, tg_chat_id))


def main():
    env = Env()
    env.read_env()
    devman_token = env.str("DEVMAN_TOKEN")
    tg_bot_token = env("TG_BOT_TOKEN")
    tg_bot_logger_token = env("TG_BOT_LOGGER_TOKEN")
    tg_chat_id = env("TG_CHAT_ID")
    params = {}

    config_logger(tg_bot_logger_token, tg_chat_id, logger)

    try:
        bot = telegram.Bot(token=tg_bot_token)
        check_reviews(devman_token, params, bot, tg_chat_id, logger)
    except Exception as error:
        logger.exception(error)


if __name__ == "__main__":
    main()

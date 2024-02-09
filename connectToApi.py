from time import sleep

import requests
import telegram

from textwrap import dedent
from retry import retry
from environs import Env


def check_api_devman(token):
    """
    :param token: str
    :return: json
    """
    url = "https://dvmn.org/api/long_polling/"

    header = {
        "Authorization": f"Token {token}"
    }
    response = requests.get(url, headers=header, timeout=20)
    response.raise_for_status()
    return response.json()


@retry(requests.exceptions.ReadTimeout, delay=30)
def check_reviews(token, params, bot, tg_chat_id):
    """

    :param token: str Token for connect to devman api
    :param params: dict empty
    :param bot: Token for connect to Telegram
    :param tg_chat_id: Personal id for chatting with bot.
    :return:
    """
    while True:
        reviews = check_api_devman(token)
        sleep(30)

        if reviews['status'] == 'timeout':
            server_timestamp = reviews['timestamp_to_request']
            params = {
                'timestamp': int(server_timestamp),
            }
        else:
            current_review = reviews['new_attempts'][0]
            if current_review['is_negative']:
                bot.send_message(chat_id=tg_chat_id,
                                 text=dedent(f"""
                                            Преподаватель проверил работу! {current_review['lesson_title']},
                                            Есть ошибки.
                                            Ссылка на работу {current_review['lesson_url']}
                                            """),)
            else:
                bot.send_message(chat_id=tg_chat_id,
                                 text=dedent(f"""
                                            Преподаватель проверил работу {current_review["lesson_title"]},
                                            Всё в порядкею
                                            """))


def main():
    env = Env()
    env.read_env()

    devman_token = env.str('DEVMAN_TOKEN')
    tg_bot_token = env('TG_BOT_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    params = {}
    bot = telegram.Bot(token=tg_bot_token)
    check_reviews(devman_token, params, bot, tg_chat_id)


if __name__ == "__main__":
    main()

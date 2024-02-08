import pprint
from time import sleep

import requests
from retry import retry
from environs import Env


@retry((requests.exceptions.ReadTimeout, ConnectionError), delay=30)
def check_api_devman(token):
    """
    :param token: str
    :return: str
    """
    url = "https://dvmn.org/api/long_polling/"

    header = {
        "Authorization": f"Token {token}"
    }
    response = requests.get(url, headers=header)
    response.raise_for_status()
    server_response = response.json()

    while True:
        if server_response['status'] == 'found':
            server_timestamp = server_response['last_attempt_timestamp']
        else:
            server_timestamp = server_response['timestamp_to_request']

        params = {
            'timestamp': int(server_timestamp),
        }

        response = requests.get(url, headers=header, params=params, timeout=90)

        response.raise_for_status()
        server_response = response.json()
        pprint.pprint(server_response)
        sleep(30)

    return pprint.pprint(params)


def main():
    env = Env()
    env.read_env()

    token = env("TOKEN")

    works = check_api_devman(token)


if __name__ == "__main__":
    main()

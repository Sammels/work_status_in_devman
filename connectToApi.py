import pprint
import requests
from environs import Env


def connect_to_devman_api(url: str, header: dict) -> str:
    """
    Function use api-key for connect to Devman api
    :return: json
    """
    response = requests.get(url, headers=header)
    response.raise_for_status()

    return response.json()


def long_pooling_devman(url, header):
    response = requests.get(url, headers=header, timeout=90)
    response.raise_for_status()
    server_response = response.json()

    server_timestamp = server_response['last_attempt_timestamp']

    params = {
        'timestamp': int(server_timestamp),
    }

    return pprint.pprint(params)


def main():
    env = Env()
    env.read_env()

    token = env("TOKEN")
    user_review_url = "https://dvmn.org/api/user_reviews/"
    long_pooling_url = "https://dvmn.org/api/long_polling/"

    header = {
        "Authorization": f"Token {token}"
    }

    # works = connect_to_devman_api(user_review_url, token, header)
    # pprint.pprint(works)

    works = long_pooling_devman(long_pooling_url, header)
    pprint.pprint(works)


if __name__ == "__main__":
    main()

import pprint
import requests
from environs import Env


def connect_to_api(url: str, token: str) -> str:
    """
    Function use api-key for connect to Devman api
    :return: str
    """
    header = {
        "Authorization": f"Token {token}"
    }

    response = requests.get(url, headers=header)
    response.raise_for_status()

    return response.json()


def main():
    env = Env()
    env.read_env()

    token = env("TOKEN")
    url = "https://dvmn.org/api/user_reviews/"

    test = connect_to_api(url, token)
    pprint.pprint(test)


if __name__ == "__main__":
    main()

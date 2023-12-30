import requests
from settings import app_settings as appset


def make_api_request(url, params):
    try:
        # Make a GET request
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the response content (JSON data in this case)
            return response.json()
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_list_categories():
    api_url = "https://api.tgstat.ru/database/categories"
    api_params = {"token": appset.tgstat_token}
    print(make_api_request(api_url, api_params))


def get_list_channels():
    api_url = "https://api.tgstat.ru/channels/search"
    api_params = {"token": appset.tgstat_token,
                  "peer_type": "channel",  # Искать только каналы
                  "country": "ru",  # (обязательный) География канала (страна)
                  "category": "crypto",  # Категория
                  "limit": 250,  # Количество каналов в ответе
                  }
    print(make_api_request(api_url, api_params))


def get_channel_stat(channel_tgstat_id):
    api_url = "https://api.tgstat.ru/channels/stat"
    api_params = {"token": appset.tgstat_token,
                  "channelId": channel_tgstat_id,  # Искать только каналы
                  "country": "ru",  # (обязательный) География канала (страна)
                  "category": "crypto",  # Категория
                  "limit": 100,  # Количество каналов в ответе
                  }
    print(make_api_request(api_url, api_params))


if __name__ == "__main__":
    # get_list_categories()
    get_list_channels()
    # get_channel_stat("@FORBESRUSSIAllllIIl")

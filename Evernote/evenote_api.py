from evernote.api.client import EvernoteClient
from settings import app_settings as appset
from urllib import request


def get_oauth_token():
    client = EvernoteClient(
        consumer_key=appset.evernote_key,
        consumer_secret=appset.evernote_secret,
        sandbox=False  # Default: True
    )
    request_token = client.get_request_token('https://dmitrybobrovsky.ru')
    print(request_token)
    print(client.get_authorize_url(request_token))
    access_token = client.get_access_token(
        request_token['oauth_token'],
        request_token['oauth_token_secret'],
        appset.oauth_verifier
    )
    print(access_token)


if __name__ == '__main__':
    get_oauth_token()
    # get_access_token()
"""
В результате получил ответ от сервера html страницу:
Oops, we encountered an error.
Sorry, we've encountered an unexpected error.
Так я и не смог авторизоваться.
"""

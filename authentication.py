import json

from spotipy import CacheHandler
from spotipy.oauth2 import SpotifyOAuth

from database import get_user_token, add_user_token

SECRETS_FILE = 'secrets.txt'


def get_secrets() -> (str, str):
    file = open(SECRETS_FILE)
    client_id = file.readline().replace('\n', '')
    client_secret = file.readline().replace('\n', '')
    return client_id, client_secret


def get_authentication(scope: str, username: str) -> SpotifyOAuth:
    # Get client ID and secret
    secrets = get_secrets()

    # Get cache handler
    ch = DatabaseCacheHandler(username)

    # Get Authentication object
    return SpotifyOAuth(scope=scope,
                        client_id=secrets[0],
                        client_secret=secrets[1],
                        redirect_uri="http://localhost:8080",
                        cache_handler=ch
                        )


class DatabaseCacheHandler(CacheHandler):
    def __init__(self, username: str):
        self.username = username

    def get_cached_token(self):
        token = get_user_token(self.username)
        if token is None:
            return None
        return json.loads(token)

    def save_token_to_cache(self, token_info):
        add_user_token(self.username, json.dumps(token_info))


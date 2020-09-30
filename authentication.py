import spotipy
from spotipy.oauth2 import SpotifyOAuth

SECRETS_FILE = 'secrets.txt'


def get_secrets() -> (str, str):
    file = open(SECRETS_FILE)
    client_id = file.readline().replace('\n', '')
    client_secret = file.readline().replace('\n', '')
    return client_id, client_secret


def get_authentication(scope: str) -> SpotifyOAuth:
    # Get client ID and secret
    secrets = get_secrets()

    # Get Authentication object
    return SpotifyOAuth(scope=scope,
                        client_id=secrets[0],
                        client_secret=secrets[1],
                        redirect_uri="http://localhost")

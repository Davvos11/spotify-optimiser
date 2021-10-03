import time

import flask
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "user-read-playback-state, playlist-modify-private"
REDIRECT_URI = "http://localhost:8080/callback"
SECRETS_FILE = 'secrets.txt'


def get_secrets() -> (str, str):
    file = open(SECRETS_FILE)
    client_id = file.readline().replace('\n', '')
    client_secret = file.readline().replace('\n', '')
    return client_id, client_secret


SECRETS = get_secrets()


def get_authentication() -> SpotifyOAuth:
    # Get Authentication object
    return create_oauth()


def get_new_token(code: str):
    oauth = create_oauth()

    return oauth.get_access_token(code)


# Checks to see if token is valid and gets a new token if not
def get_spotipy(session: flask.session):
    token = session.get("token", {})

    # Checking if the session already has a token stored
    if session.get('token', False):
        # Checking if token has expired
        now = int(time.time())
        is_token_expired = session.get('token').get('expires_at') - now < 60

        # Refreshing token if it has expired
        if is_token_expired:
            # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you
            # reuse a SpotifyOAuth object
            sp_oauth = create_oauth()
            token = sp_oauth.refresh_access_token(session.get('token').get('refresh_token'))

        # Update the session
        session["token"] = token

    # Return the Spotipy object
    return spotipy.Spotify(auth=session.get('token').get('access_token'))


def create_oauth():
    return SpotifyOAuth(scope=SCOPE,
                        client_id=SECRETS[0],
                        client_secret=SECRETS[1],
                        redirect_uri=REDIRECT_URI,
                        open_browser=False
                        )

import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "user-library-read"
SECRETS_FILE = 'secrets.txt'
AUTH_FILE = 'authentication.pkl'


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


if __name__ == '__main__':
    auth_manager = get_authentication(SCOPE)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])

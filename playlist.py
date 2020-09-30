import spotipy
import pickle

from datetime import datetime


class Playlist:
    def __init__(self, spotify: spotipy.Spotify) -> None:
        self.spotify = spotify
        self.id = None
        self._create()

    def _create(self):
        now = datetime.now()
        name = "Not-skipped " + now.strftime("%d %B")
        description = "Created by Spotify Optimiser on " + now.strftime("%x %X") + " Author: Davvos11"

        user = self.spotify.current_user()
        created = self.spotify.user_playlist_create(user['id'], name, public=False, description=description)
        self.id = created['id']

    def add(self, track_id):
        self.spotify.playlist_add_items(self.id, [track_id])


def detect_saved_playlist(filename: str) -> bool:
    try:
        # Try to load the authenticator that has been saved before
        with open(filename, 'rb') as file:
            pickle.load(file)
            return True
    except FileNotFoundError or ImportError:
        return False


def load_playlist(filename: str, spotify: spotipy.Spotify, force_new=False) -> (Playlist, bool):
    if not force_new:
        try:
            # Try to load the authenticator that has been saved before
            with open(filename, 'rb') as file:
                return pickle.load(file), False
        except FileNotFoundError or ImportError:
            pass

    # Create a new playlist, if desired or if none could be found
    playlist = Playlist(spotify)
    # Save the playlist to use next time
    with open(filename, 'wb') as file:
        pickle.dump(playlist, file)

    return playlist, True

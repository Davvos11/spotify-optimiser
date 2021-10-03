import traceback
import spotipy

import authentication

from time import sleep

from database import start_song, skip_song

SCOPE = "user-read-playback-state, playlist-modify-private"
USERNAME = "username"


def main():
    # Login to Spotify
    print("Connecting to Spotify")
    auth = authentication.get_authentication(SCOPE, USERNAME)
    sp = spotipy.Spotify(auth_manager=auth)

    # Main loop:
    try:
        while True:
            # Wait until the user starts playing something
            x = True
            while True:
                playback = sp.current_playback()
                if playback and playback['is_playing'] and playback['item']:
                    break
                if x:
                    print("Waiting until playback starts...")
                    x = False
                sleep(1)

            # Get current track info
            current = sp.current_playback()
            track_id = current['item']['id']
            artists = ", ".join([a['name'] for a in current['item']['artists']])
            playlist_uri = current['context']['uri']\
                if current['context']['type'] == 'playlist' else None
            print(f"Now playing: {artists} - {current['item']['name']}")

            # Update the database (start of a song)
            # TODO fix USERNAME, use session or something
            song = start_song(USERNAME, playlist_uri, track_id)

            finished = False
            # Wait until track changes (either skip or end of song)
            try:
                while (playback := sp.current_playback())['item']['id'] == track_id:
                    # Calculate how long it takes until the end of the track
                    time_left = playback['item']['duration_ms'] - playback['progress_ms']
                    # If we are in the last few seconds of the track, we count it as not skipped
                    if time_left <= 5000:
                        finished = True
                    # Wait a second (to improve performance)
                    sleep(1)
            except TypeError:
                # If playback stops (client disconnects) sp.current_playback will be None
                continue  # Go back to waiting

            # If the track did not finish, it must've been skipped, thus we update the database
            if not finished:
                skip_song(song)

    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        main()


if __name__ == '__main__':
    main()

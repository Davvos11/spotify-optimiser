import traceback
import spotipy

import authentication
import playlist as pl
import functions

from time import sleep

SCOPE = "user-read-playback-state, playlist-modify-private"
PLAYLIST_FILE = "playlist.pkl"


def main():
    # Login to Spotify
    print("Connecting to Spotify")
    auth = authentication.get_authentication(SCOPE)
    sp = spotipy.Spotify(auth_manager=auth)

    # If there is a playlist to restore but the user does not want to, force a new playlist
    force = pl.detect_saved_playlist(PLAYLIST_FILE) \
        and not functions.get_bool("Do you want to use the same playlist as last time?")

    playlist, created = pl.load_playlist(PLAYLIST_FILE, sp, force)
    print("Started session " + ("and created a new playlist" if created else "with the same playlist"))

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
            print("Now playing: {artist} - {title}".format(artist=artists, title=current['item']['name']))

            finished = False
            # Wait until track changes (either skip or end of song)
            try:
                while (p := sp.current_playback())['item']['id'] == track_id:
                    # Calculate how long it takes until the end of the track
                    time_left = p['item']['duration_ms'] - p['progress_ms']
                    # If we are in the last few seconds of the track, we count it as not skipped
                    if time_left <= 5000:
                        finished = True
                    # Wait a second (to improve performance)
                    sleep(1)
            except TypeError:
                # If playback stops (client disconnects) sp.current_playback will be None
                continue  # Go back to waiting

            # If the track did not finish, it must've been skipped, thus we do not add it to our playlist
            if finished:
                print("   Finished, adding to playlist")
                playlist.add(track_id)
            else:
                print("   Skipped, not adding")
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        main()


if __name__ == '__main__':
    main()

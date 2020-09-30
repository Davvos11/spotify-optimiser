import spotipy
import authentication
from time import sleep

SCOPE = "user-read-playback-state, user-read-recently-played"

if __name__ == '__main__':
    # Login to Spotify
    auth = authentication.get_authentication(SCOPE)
    sp = spotipy.Spotify(auth_manager=auth)

    # Main loop:
    while True:
        # Wait until the user starts playing something
        while True:
            playback = sp.current_playback()
            if playback and playback['is_playing']:
                break
            print("Waiting until playback starts...")

        # Get current track info
        current = sp.current_playback()
        track_id = current['item']['id']
        artists = ", ".join([a['name'] for a in current['item']['artists']])
        print("Now playing: {artist} - {title}".format(artist=artists, title=current['item']['name']))

        finished = False
        # Wait until track changes (either skip or end of song)
        while (p := sp.current_playback())['item']['id'] == track_id:
            # Calculate how long it takes until the end of the track
            time_left = p['item']['duration_ms'] - p['progress_ms']
            # If we are in the last few seconds of the track, we count it as not skipped
            if time_left <= 5000:
                finished = True
            # Wait a second (to improve performance)
            sleep(1)

        # If the track did not finish, it must've been skipped, thus we do not add it to our playlist
        if finished:
            print("Finished")
        else:
            print("Skipped")

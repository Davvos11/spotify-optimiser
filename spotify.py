import threading
import traceback

import spotipy

from time import sleep

from database import start_song, skip_song, get_user

SCOPE = "user-read-playback-state, playlist-modify-private"


def listen(sp: spotipy.Spotify):
    try:
        # Get the current user id
        user_id = sp.current_user()["id"]
        # Check if the user is not disabled
        user = get_user(user_id)
        if not user.enabled:
            return

        # Main loop:
        while True:
            # Wait until the user starts playing something
            x = True
            while True:
                playback = sp.current_playback()
                if playback and playback['is_playing'] and playback['item']:
                    break
                if x:
                    print(f"{user_id}: Waiting until playback starts...")
                    x = False
                sleep(1)

            # Get current track info
            current = sp.current_playback()
            track_id = current['item']['id']
            artists = ", ".join([a['name'] for a in current['item']['artists']])
            playlist_uri = current['context']['uri'] \
                if current['context']['type'] == 'playlist' else None
            print(f"{user_id}: Now playing: {artists} - {current['item']['name']}")

            # Update the database (start of a song)
            song = start_song(user_id, playlist_uri, track_id)

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

    except Exception:
        traceback.print_exc()
        # listen(sp)


def start_listening(sp: spotipy.Spotify):
    threading.Thread(target=listen, args=[sp]).start()


def get_song_info(sp: spotipy.Spotify, ids: [str]):
    result = []
    for track in sp.tracks(tracks=ids)["tracks"]:
        result.append({
            "name": track["name"],
            "artist": ", ".join([artist["name"] for artist in track["artists"]]),
            "img": track["album"]["images"][0]["url"],
            "uri": track["external_urls"]["spotify"]
        })
    return result


def get_playlist_info(sp: spotipy.Spotify, ids: [str]):
    result = []
    for pid in ids:
        playlist = sp.playlist(pid)
        result.append({
            "name": playlist["name"],
            "img": playlist["images"][0]["url"]
        })
    return result


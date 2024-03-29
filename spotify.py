import threading
import traceback
from typing import Set

import spotipy

from time import sleep

from requests import ReadTimeout
from spotipy import SpotifyException

from authentication import get_spotipy_from_token
from database import start_song, skip_song, get_user, enable_user

SCOPE = "user-read-playback-state, playlist-modify-private"

listening_to: Set[int] = set()


def listen(sp: spotipy.Spotify):
    user_id = None

    while True:
        try:
            # Get the current user id
            user_id = sp.current_user()["id"]
            # Check if the user is not disabled
            user = get_user(user_id)
            if not user.enabled:
                return
            # Check if we are not already listening to this user
            if user_id in listening_to:
                return
            listening_to.add(user_id)

            playlist_id = None
            playlist_title = ""

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
                    sleep(10)

                # Get current track info
                current = sp.current_playback()
                track_id = current['item']['id']
                artists = ", ".join([a['name'] for a in current['item']['artists']])
                title = current['item']['name']
                cover_art = current['item']['album']['images'][0]['url']
                if current['context'] is not None and current['context']['type'] == 'playlist':
                    # If we changed to a new playlist, update the playlist
                    playlist_id = current['context']['uri'].replace("spotify:playlist:", "")
                    playlist = get_playlist_info(sp, [playlist_id])[0]
                    playlist_title = playlist['name']
                print(f"{user_id}: Now playing: {artists} - {title}")

                # Update the database (start of a song)
                song = start_song(user_id, playlist_id, track_id, title, playlist_title, artists, cover_art)

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

        except ReadTimeout:
            print(f"{user_id}: Timed out, reconnecting")
            pass
        except SpotifyException as e:
            # Check if this is an expired access token
            if e.http_status == 401:
                # Get the users token
                user = get_user(user_id)
                # Get a new Spotify session
                sp = get_spotipy_from_token(user.token)
        except Exception:
            traceback.print_exc()


def start_listening(sp: spotipy.Spotify):
    # Ensure the user is enabled
    user_id = sp.current_user()["id"]
    enable_user(user_id, True)
    # Start a thread
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


def add_to_playlist(sp: spotipy.Spotify, song_ids: [str], playlist_id: str):
    sp.playlist_add_items(playlist_id, [f"spotify:track:{sid}" for sid in song_ids])


def remove_from_playlist(sp: spotipy.Spotify, song_ids: [str], playlist_id: str):
    sp.playlist_remove_all_occurrences_of_items(playlist_id, [f"spotify:track:{sid}" for sid in song_ids])


def add_to_new_playlist(sp: spotipy.Spotify, song_ids: [str], name: str):
    query = sp.user_playlist_create(sp.me()["id"], name)
    playlist_id = query["id"]
    add_to_playlist(sp, song_ids, playlist_id)

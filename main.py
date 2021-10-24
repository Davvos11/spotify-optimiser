from flask import Flask, session, redirect, request
from flask_restful import Resource, Api, reqparse

# Create a Flask server
from authentication import get_authentication, get_spotipy, get_new_token, set_token, get_spotipy_from_token
from database import get_tokens, get_skip_stats, ignore_entries, get_user
from spotify import start_listening, get_song_info, get_playlist_info, add_to_playlist, remove_from_playlist, \
    add_to_new_playlist

app = Flask(__name__)
app.config.update(SECRET_KEY='$@F3br3YgGYDRX',
                  ENV='development'
                  )
api = Api(app)


class Login(Resource):
    @staticmethod
    def get():
        auth = get_authentication()
        # Redirect the user
        redirect_uri = auth.get_authorize_url()
        return redirect(redirect_uri)


class Callback(Resource):
    @staticmethod
    def get():
        session.clear()
        # Get the code and oauth token
        code = request.args.get('code')
        token = get_new_token(code)
        # Store in the session
        set_token(session, token)
        return redirect("/test")


class AuthResource(Resource):
    def __init__(self):
        if "token" in session:
            self.sp = get_spotipy(session)

    def dispatch_request(self, *args, **kwargs):
        # Check if there is a session token
        if "token" in session:
            # Continue normally
            return super().dispatch_request(*args, **kwargs)
        else:
            # Redirect to the login page
            return redirect("/login")


class Test(AuthResource):
    def get(self):
        return self.sp.current_user()


class Enable(AuthResource):
    def post(self):
        start_listening(self.sp)
        return '', 204

    def get(self):
        user_id = self.sp.current_user()["id"]
        user = get_user(user_id)
        return user.enabled


class Stats(AuthResource):
    def get(self):
        user_id = self.sp.current_user()["id"]
        return get_skip_stats(user_id)


class Songs(AuthResource):
    def get(self):
        ids = request.args.get('ids').split(",")
        return get_song_info(self.sp, ids)


class Playlists(AuthResource):
    def get(self):
        ids = request.args.get('ids').split(",")
        return get_playlist_info(self.sp, ids)


apply_parser = reqparse.RequestParser()
apply_parser.add_argument('playlist', type=str, help='Spotify playlist ID')
apply_parser.add_argument('songs', type=str, help='Spotify song IDs')
apply_parser.add_argument('name', type=str, help='Name of the new playlist')


class ApplyChanges(AuthResource):
    def put(self):
        """ Add songs to existing playlist """
        args = apply_parser.parse_args()
        song_ids = args['songs'].split(",")
        playlist_id = args['playlist']
        add_to_playlist(self.sp, song_ids, playlist_id)
        return '', 204

    def delete(self):
        """ Remove songs from playlist """
        args = apply_parser.parse_args()
        song_ids = args['songs'].split(",")
        playlist_id = args['playlist']
        remove_from_playlist(self.sp, song_ids, playlist_id)
        return '', 204

    def post(self):
        """ Add songs to new playlist """
        args = apply_parser.parse_args()
        song_ids = args['songs'].split(",")
        name = args['name']
        add_to_new_playlist(self.sp, song_ids, name)
        return '', 204


api.add_resource(Login, "/login")
api.add_resource(Callback, "/callback")
api.add_resource(Test, "/test")
api.add_resource(Enable, "/enable")
api.add_resource(Stats, "/stats")
api.add_resource(Songs, "/songs")
api.add_resource(Playlists, "/playlists")
api.add_resource(ApplyChanges, "/apply")


def main():
    # Load previous sessions and continue listening
    for token in get_tokens():
        sp = get_spotipy_from_token(token)
        # Start listening
        start_listening(sp)

    # Start the app
    app.run(debug=False, port=8080)


if __name__ == '__main__':
    main()

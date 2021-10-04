from flask import Flask, session, redirect, request
from flask_restful import Resource, Api

# Create a Flask server
from authentication import get_authentication, get_spotipy, get_new_token, set_token, get_spotipy_from_token
from database import get_tokens
from spotify import start_listening

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
        return redirect("/")


class AuthResource(Resource):
    def dispatch_request(self, *args, **kwargs):
        # Check if there is a session token
        if "token" in session:
            # Continue normally
            return super().dispatch_request(*args, **kwargs)
        else:
            # Redirect to the login page
            return redirect("/login")


class Test(AuthResource):
    @staticmethod
    def get():
        sp = get_spotipy(session)
        return sp.current_user()


class Enable(AuthResource):
    @staticmethod
    def get():
        sp = get_spotipy(session)
        start_listening(sp)
        return None


api.add_resource(Login, "/login")
api.add_resource(Callback, "/callback")
api.add_resource(Test, "/")
api.add_resource(Enable, "/enable")


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

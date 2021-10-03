from typing import Dict

import spotipy
from flask import Flask, session, redirect, request
from flask_restful import Resource, Api

# Create a Flask server
from authentication import get_authentication, get_spotipy, get_new_token

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
        session["token"] = token
        return redirect("/")


class Test(Resource):
    @staticmethod
    def get():
        sp = get_spotipy(session)
        return sp.current_user()


api.add_resource(Login, "/login")
api.add_resource(Callback, "/callback")
api.add_resource(Test, "/")

if __name__ == '__main__':
    app.run(debug=True, port=8080)


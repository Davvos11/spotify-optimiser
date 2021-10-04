import json
from typing import Optional

from peewee import *
from playhouse.shortcuts import model_to_dict

db = SqliteDatabase('database.sqlite')


class BaseModel(Model):
    class Meta:
        database = db

    meta = Meta


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    enabled = BooleanField(default=True)


class Token(BaseModel):
    token = CharField(primary_key=True)
    token_json = CharField()


class SongInstance(BaseModel):
    user = ForeignKeyField(User, backref='song_instances')
    playlist_uri = CharField()
    track_id = CharField()
    listen_count = IntegerField(default=1)
    skip_count = IntegerField(default=0)

    class Meta(BaseModel.meta):
        primary_key = CompositeKey('user', 'playlist_uri', 'track_id')


# Connect to the database and create tables
try:
    db.connect()
    db.create_tables([User, Token, SongInstance])
except OperationalError:
    # Can happen if the database is already connected to
    pass


def add_token(token):
    try:
        Token.create(token=token.get('access_token'), token_json=json.dumps(token))
    except IntegrityError:
        pass


def replace_token(old, new):
    query = Token.delete().where(Token.token == old.get('access_token'))
    query.execute()
    add_token(new)


def get_tokens():
    query = Token.select()
    return [json.loads(token.token_json) for token in query]


def get_user(user_id: int) -> User:
    try:
        return User.get(User.user_id == user_id)
    except User.DoesNotExist:
        return User.create(user_id=user_id)


def start_song(user_id: int, playlist_uri: Optional[str], track_id: str) -> SongInstance:
    # When we are not listening to a playlist, make the playlist field empty
    if playlist_uri is None:
        playlist_uri = ""
    # Get the user object
    user = get_user(user_id)

    try:
        # Create an instance and return it
        song = SongInstance.create(user=user, playlist_uri=playlist_uri, track_id=track_id)
        return song
    except IntegrityError:
        # If the song instance already exists, update it
        query = SongInstance.update(listen_count=SongInstance.listen_count + 1). \
            where(SongInstance.user == user,
                  SongInstance.playlist_uri == playlist_uri,
                  SongInstance.track_id == track_id
                  )
        query.execute()
        # Return the instance
        return SongInstance.get(SongInstance.user == user,
                                SongInstance.playlist_uri == playlist_uri,
                                SongInstance.track_id == track_id
                                )


def skip_song(song_instance: SongInstance):
    query = SongInstance.update(skip_count=SongInstance.skip_count + 1). \
        where(SongInstance.user == song_instance.user,
              SongInstance.playlist_uri == song_instance.playlist_uri,
              SongInstance.track_id == song_instance.track_id
              )
    query.execute()


def get_skip_stats(user_id: int):
    user = User.get(User.user_id == user_id)
    items = SongInstance.select().where(SongInstance.user == user)
    return [model_to_dict(item) for item in items]

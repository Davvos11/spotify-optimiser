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
    enabled = BooleanField(default=False)


class Token(BaseModel):
    token = CharField(primary_key=True)
    token_json = CharField()
    user = ForeignKeyField(User, backref='token')


class SongInstance(BaseModel):
    user = ForeignKeyField(User, backref='song_instances')
    playlist_id = CharField()
    track_id = CharField()
    title = CharField()
    playlist_title = CharField()
    artists = CharField()
    cover_art = CharField()
    listen_count = IntegerField(default=1)
    skip_count = IntegerField(default=0)

    class Meta(BaseModel.meta):
        primary_key = CompositeKey('user', 'playlist_id', 'track_id')


# Connect to the database and create tables
try:
    db.connect()
    db.create_tables([User, Token, SongInstance])
except OperationalError:
    # Can happen if the database is already connected to
    pass


def add_token(token, user_id: int):
    try:
        Token.create(token=token.get('access_token'), token_json=json.dumps(token), user_id=user_id)
    except IntegrityError as e:
        # TODO check what specific IntegrityError this is
        print(e)


def replace_token(old, new, user_id: int):
    query = Token.delete().where(Token.token == old.get('access_token'))
    query.execute()
    add_token(new, user_id)


def get_tokens():
    query = Token.select()
    return [json.loads(token.token_json) for token in query]


def get_user(user_id: int) -> User:
    try:
        return User.get(User.user_id == user_id)
    except User.DoesNotExist:
        return User.create(user_id=user_id)


def start_song(user_id: int, playlist_id: Optional[str], track_id: str,
               title: str, playlist_title: str, artists: str, cover_art: str) -> SongInstance:
    # When we are not listening to a playlist, make the playlist field empty
    if playlist_id is None:
        playlist_id = ""
    # Get the user object
    user = get_user(user_id)

    try:
        # Create an instance and return it
        song = SongInstance.create(user=user, playlist_id=playlist_id, track_id=track_id,
                                   title=title, playlist_title=playlist_title, artists=artists, cover_art=cover_art)
        return song
    except IntegrityError:
        # If the song instance already exists, update it
        query = SongInstance.update(listen_count=SongInstance.listen_count + 1). \
            where(SongInstance.user == user,
                  SongInstance.playlist_id == playlist_id,
                  SongInstance.track_id == track_id
                  )
        query.execute()
        # Return the instance
        return SongInstance.get(SongInstance.user == user,
                                SongInstance.playlist_id == playlist_id,
                                SongInstance.track_id == track_id
                                )


def skip_song(song_instance: SongInstance):
    query = SongInstance.update(skip_count=SongInstance.skip_count + 1). \
        where(SongInstance.user == song_instance.user,
              SongInstance.playlist_id == song_instance.playlist_id,
              SongInstance.track_id == song_instance.track_id
              )
    query.execute()


def get_skip_stats(user_id: int):
    user = User.get(User.user_id == user_id)
    items = SongInstance.select().where(SongInstance.user == user)
    return [model_to_dict(item) for item in items]


def ignore_entries(song_ids: [str], playlist_id: str, user_id: int):
    # Get the user object
    user = get_user(user_id)

    for song_id in song_ids:
        query = SongInstance.update(ignored=True). \
            where(SongInstance.user == user,
                  SongInstance.playlist_id == playlist_id,
                  SongInstance.track_id == song_id)
        query.execute()


def enable_user(user_id: str, enabled: bool):
    query = User.update(enabled=enabled).where(User.user_id == user_id)
    query.execute()

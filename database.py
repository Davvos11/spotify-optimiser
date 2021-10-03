from typing import Optional

from peewee import *

db = SqliteDatabase('database.sqlite')


class BaseModel(Model):
    class Meta:
        database = db
    meta = Meta


class User(BaseModel):
    username = CharField(unique=True)
    token = CharField()


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
    db.create_tables([User, SongInstance])
except OperationalError:
    # Can happen if the database is already connected to
    pass


def add_user_token(username: str, token: str):
    try:
        User.create(username=username, token=token)
    except IntegrityError:
        # If the user already exists, update it
        query = User.update(token=token).where(User,username == username)
        query.execute()


def get_user_token(username: str) -> Optional[str]:
    try:
        user = User.get(User.username == username)
        return user.token
    except User.DoesNotExist:
        return None


def start_song(username: str, playlist_uri: Optional[str], track_id: str) -> SongInstance:
    # When we are not listening to a playlist, make the playlist field empty
    if playlist_uri is None:
        playlist_uri = ""
    # Get the user object
    user = User.get(User.username == username)

    try:
        # Create an instance and return it
        song = SongInstance.create(user=user, playlist_uri=playlist_uri, track_id=track_id)
        song.save()
        return song
    except IntegrityError:
        # If the song instance already exists, update it
        query = SongInstance.update(listen_count=SongInstance.listen_count + 1).\
            where(SongInstance.user == user,
                  SongInstance.playlist_uri == playlist_uri,
                  SongInstance.track_id == track_id
                  )
        query.execute()
        # Return the instance
        return SongInstance.get(user=user, playlist_uri=playlist_uri, track_id=track_id)


def skip_song(song_instance: SongInstance):
    query = SongInstance.update(skip_count=SongInstance.skip_count + 1).\
        where(SongInstance.user == song_instance.user,
              SongInstance.playlist_uri == song_instance.playlist_uri,
              SongInstance.track_id == song_instance.track_id
              )
    query.execute()


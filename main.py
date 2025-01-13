from typing import Union
from pydantic import BaseModel
import datetime
from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship

engine = create_engine("sqlite:///database.db")

from fastapi import FastAPI,  Depends, HTTPException
from datetime import date

app = FastAPI()

def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

class SongArtistLink(SQLModel, table=True):
    song_id: int = Field(foreign_key="song.id", primary_key=True)
    artist_id: int = Field(foreign_key="artist.id", primary_key=True)

class Song(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    album_id: int = Field(foreign_key="album.id")
    release_date: datetime.date
    votes: int = 0
    artists: list["Artist"] = Relationship(back_populates="songs", link_model=SongArtistLink)
    album: "Album" = Relationship(back_populates="songs")

class Artist(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    albums: list["Album"] = Relationship(back_populates="artist")
    songs: list["Song"] = Relationship(back_populates="artists", link_model=SongArtistLink)
    birth_date: datetime.date
    ethnicity: str
    birth_place: str

class Album(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    artist_id: int = Field(foreign_key="artist.id")
    release_date: datetime.date
    songs: list["Song"] = Relationship(back_populates="album")
    artist: "Artist" = Relationship(back_populates="albums")

@app.post("/artist/")
def create_artist(artist: Artist, session: Session = Depends(get_session)):
    try:
        artist.birth_date = date.fromisoformat(artist.birth_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    session.add(artist)
    session.commit()
    return artist

@app.get("/artist/{artist_id}")
def read_artist(artist_id: int, session: Session = Depends(get_session)):
    artist = session.get(Artist, artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@app.get("/artist")
def read_artists(session: Session = Depends(get_session)):
    artists = session.exec(select(Artist)).all()
    return artists

@app.post("/album/")
def create_album(album: Album, session: Session = Depends(get_session)):
    try:
        album.release_date = date.fromisoformat(album.release_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    session.add(album)
    session.commit()
    return album

@app.get("/album/{album_id}")
def read_album(album_id: int, session: Session = Depends(get_session)):
    album = session.get(Album, album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@app.get("/album")
def read_albums(session: Session = Depends(get_session)):
    albums = session.exec(select(Album)).all()
    return albums

@app.post("/song/")
def create_song(song: Song, session: Session = Depends(get_session)):
    try:
        song.release_date = date.fromisoformat(song.release_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    session.add(song)
    session.commit()
    return song

@app.get("/song/{song_id}")
def read_song(song_id: int, session: Session = Depends(get_session)):
    song = session.get(Song, song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@app.get("/song")
def read_songs(session: Session = Depends(get_session)):
    songs = session.exec(select(Song)).all()
    return songs

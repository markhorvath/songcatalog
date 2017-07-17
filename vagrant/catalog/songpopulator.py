#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 10:56:26 2017

@author: markhorvath
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from songsdb_setup import Base, Song, Tags, Names

engine = create_engine('sqlite:///songs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


f = open('mainTable.txt', 'r')

lines = f.readlines()

for line in lines:
    data = line.split("|")
    ID = data[0]
    key = data[1]
    year = data[2]
    composer = data[3]
    bpm = data[4]
    timesig = data[5]
    source = data[6]

    
    song1 = Song(id=ID, key=key, year=year, composer = composer,
                 bpm=bpm, timesig=timesig, source=source)
    session.add(song1)
    session.commit()

f = open('nameTable.txt', 'r')

lines = f.readlines()

for line in lines:
    data = line.split("|")
    ID = id
    name = data[1]
    song_id = data[0]
    
    name1 = Names(name = name, song_id = song_id)
    session.add(name1)
    session.commit()
    
f = open('tagTable.txt', 'r')

lines = f.readlines()

for line in lines:
    data = line.split("|")
    tags = data[1]
    song_id = data[0]
    
    tag1 = Tags(tags = tags, song_id = song_id)
    session.add(tag1)
    session.commit()
    
    
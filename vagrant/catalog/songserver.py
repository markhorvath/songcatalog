#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 12:58:48 2017

@author: markhorvath
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from songsdb_setup import Base, Song, Tags, Names

engine = create_engine('sqlite:///songs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

def getCategory(query):
    results = session.query(Tags.tags).filter(Tags.tags.like('%query%')).all()
    return results



results = session.query(Tags.tags, Tags.song_id).filter(Tags.tags.like('%hungarian%')).all()
print results


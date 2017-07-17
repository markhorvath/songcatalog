#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 10:54:33 2017

@author: markhorvath
"""

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class Song(Base):
    __tablename__ = 'allsongs'
    
    id = Column(Integer, primary_key = True)
    key = Column(String, nullable = False)
    year = Column(Integer, nullable = False)
    composer = Column(String, nullable = False)
    bpm = Column(Integer, nullable = False)
    timesig = Column(String, nullable = False)
    source = Column(String, nullable = False)
    
    
class Tags(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key = True)
    tags = Column(String, nullable = False)
    song_id = Column(Integer, ForeignKey('allsongs.id'))
    song = relationship(Song)
    
    
class Names(Base):
    __tablename__ = 'names'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    song_id = Column(Integer, ForeignKey('allsongs.id'))
    song = relationship(Song)

engine = create_engine(
        'sqlite:///songs.db')

Base.metadata.create_all(engine)
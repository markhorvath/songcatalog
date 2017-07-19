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

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False)

class Song(Base):
    __tablename__ = 'allsongs'
    
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    key = Column(String, nullable = False)
    year = Column(Integer, nullable = False)
    composer = Column(String, nullable = False)
    bpm = Column(Integer, nullable = False)
    timesig = Column(String, nullable = False)
    source = Column(String, nullable = False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    
engine = create_engine(
        'sqlite:///songs.db')

Base.metadata.create_all(engine)
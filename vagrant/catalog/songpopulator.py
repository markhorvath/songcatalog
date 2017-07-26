#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 10:56:26 2017

@author: markhorvath
"""
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker

from songsdb_setup import Base, Category, Song, User

engine = create_engine('sqlite:///songs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


f = open('mainTable.txt', 'r')

lines = f.readlines()
categories = []

User1 = User(name="Marky Mark", email="funkybunch@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Create list of distinct Categories
#for line in lines:
#    data = line.split("|")
#    category = data[3].title()
#    if category not in categories:
#        categories.append(category)
## Populate Category table
#for category in categories:
#    categoryToAdd = Category(user_id=1, name = category)
#    session.add(categoryToAdd)
#    session.commit()
## Populate Song table 
#    for line in lines:
#        data = line.split("|")
#        lineCategory = data[3].title()
#        if lineCategory == category:
#            name = data[0]
#            key = data[1]
#            year = data[2]
#            composer = data[4]
#            bpm = data[5]
#            timesig = data[6]
#            source = data[7].replace('\n', '')
#            song1 = Song(user_id=1, name = name, key=key, year=year, composer = composer,
#                         bpm=bpm, timesig=timesig, source=source, category = categoryToAdd)
#            session.add(song1)
#            session.commit()


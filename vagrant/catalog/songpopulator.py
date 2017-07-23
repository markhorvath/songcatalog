#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 10:56:26 2017

@author: markhorvath
"""
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker

from songsdb_setup import Base, Category, Song

engine = create_engine('sqlite:///songs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


f = open('mainTable.txt', 'r')

lines = f.readlines()
categories = []

# Populate the Category table
#for line in lines:
#    data = line.split("|")
#    category = data[3]
#    if category not in categories:
#        categories.append(category)
#        
#for category in categories:
#    categoryToAdd = Category(name = category)
#    session.add(categoryToAdd)
#    session.commit()
#    for line in lines:
#        data = line.split("|")
#        if data[3] == category:
#            name = data[0]
#            key = data[1]
#            year = data[2]
#            category = data[3]
#            composer = data[4]
#            bpm = data[5]
#            timesig = data[6]
#            source = data[7]
#            song1 = Song(name = name, key=key, year=year, composer = composer,
#                         bpm=bpm, timesig=timesig, source=source, category = categoryToAdd)
#            session.add(song1)
#            session.commit()

editedCategory = session.query(Category).filter(Category.name.like('Aaa%')).one()
print editedCategory.name
print editedCategory.id
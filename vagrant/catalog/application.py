#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 12:58:48 2017

@author: markhorvath
"""
from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, distinct, func, or_

from songsdb_setup import Base, Song, Tags, Names

engine = create_engine('sqlite:///songs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

@app.route('/')
@app.route('/index/')
def showCategories():
    tags = session.query(Tags).group_by(Tags.tags).all()
    return render_template('main.html', categories = tags)

@app.route('/index/<category>/')
def showCategorySongs(category):
    ids = session.query(Tags.song_id).filter(Tags.tags.like(category)).all()
    ids = [r[0] for r in ids]
    print ids
#    ids = [3,4,8,16]
    names = session.query(Names).filter(Names.song_id.in_(ids)).all()
    return render_template('categorysongs.html', songs = names, category = category)

def getCategory(query):
    results = session.query(Tags.tags).filter(Tags.tags.like('%query%')).all()
    return results

#results = session.query(Tags.tags, Tags.song_id).filter(Tags.tags.like('%hungarian%')).all()
#print results

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
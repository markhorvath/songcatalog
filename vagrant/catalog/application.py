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
from sqlalchemy import and_

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
    tags = session.query(Tags).distinct(Tags.tags).group_by(Tags.tags)
    return render_template('index.html', tags = tags)


def getCategory(query):
    results = session.query(Tags.tags).filter(Tags.tags.like('%query%')).all()
    return results

#results = session.query(Tags.tags, Tags.song_id).filter(Tags.tags.like('%hungarian%')).all()
#print results

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
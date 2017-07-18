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

# Route to main page
@app.route('/')
@app.route('/index/')
def showCategories():
    tags = session.query(Tags).group_by(Tags.tags).all()
    for i in tags:
        i.tags = i.tags.title()
    return render_template('index.html', categories = tags)

# Route to specific category songs
@app.route('/index/<category>/')
def showCategorySongs(category):
    ids = session.query(Tags.song_id).filter(Tags.tags.like(category)).all()
    #change format of ids, there's surely a better way to do this through
    #a join or subquery
    ids = [i[0] for i in ids]
    names = session.query(Names).filter(Names.song_id.in_(ids)).all()
    return render_template('categorysongs.html', songs = names, category = category)

# Route to song details
@app.route('/index/<category>/<int:song_id>/<name>')
def showSongInfo(category, song_id, name):
    song = session.query(Song).filter(Song.id == song_id).one()
    return render_template('songinfo.html', song = song, name = name)

@app.route('/index/newcategory/', methods = ['GET','POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Tags(tags = request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')

def getCategory(query):
    results = session.query(Tags.tags).filter(Tags.tags.like('%query%')).all()
    return results

#results = session.query(Tags.tags, Tags.song_id).filter(Tags.tags.like('%hungarian%')).all()
#print results

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
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

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response

from songsdb_setup import Base, Category, Song

CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///songs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Route to login
@app.route('/login/')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.
                digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE = state)
    
# Route to main page
@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).group_by(Category.name).all()
    for i in categories:
        i.name = i.name.title()
    return render_template('categories.html', categories = categories)

# Route to specific category songs
@app.route('/categories/<category>/<int:category_id>')
def showCategorySongs(category, category_id):
    songs = session.query(Song).filter(Song.category_id == category_id).all()
    return render_template('categorysongs.html', songs = songs, category = category, category_id = category_id)

# Route to song details
@app.route('/categories/<category>/<int:category_id>/<name>/<int:song_id>')
def showSongInfo(category, category_id, song_id, name):
    song = session.query(Song).filter(Song.id == song_id).one()
    return render_template('songinfo.html', song = song, name = name)

# Route to add a new category
@app.route('/category/new/', methods = ['GET','POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'])
        session.add(newCategory)
        session.commit()
        flash('New Category %s Successfully Created' % newCategory.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')

@app.route('/category/<category>/edit/', methods = ['GET', 'POST'])
def editCategory(category):
    editedCategory = session.query(Category).filter(Category.name.like(category)).one()
    oldName = editedCategory.name
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category %s Successfully Changed to %s' % (oldName, editedCategory.name))
            return redirect(url_for('showCategories'))
    else:
        return render_template('editcategory.html', category = editedCategory)

#this needs work
@app.route('/category/<category>/<name>/<int:song_id>/edit', methods = ['GET', 'POST'])
def editSong(category, name, song_id):
    currentCategory = session.query(Category).filter(Category.name == category).one()
    editedSong = session.query(Song).filter(Song.id == song_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedSong.name = request.form['name']
        if request.form['key']:
            editedSong.key = request.form['key']
        if request.form['year']:
            editedSong.year = request.form['year']
        if request.form['composer']:
            editedSong.composer = request.form['composer']
        if request.form['bpm']:
            editedSong.bpm = request.form['bpm']
        if request.form['timesig']:
            editedSong.timesig = request.form['timesig']
        session.add(editedSong)
        session.commit()
        flash('Song Successfully Edited!')
        return redirect(url_for('showCategorySongs', category = currentCategory.name,
                                category_id = currentCategory.id))
    else:
        return render_template('editsong.html', category = category,
                               song = editedSong,
                               name = editedSong.name,
                               song_id = editedSong.id)

# Route to delete a category
@app.route('/categories/<category>/<int:category_id>/delete', methods = ['GET', 'POST'])
def deleteCategory(category, category_id):
    # This only works when 'one.()' is appended, if it's all it returns a 302 error
    categoryToDelete = session.query(Category).filter(Category.id == category_id).one()
    print categoryToDelete
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showCategories', category_id = category_id))
    else:
        return render_template('deletecategory.html', category = categoryToDelete)

@app.route('/categories/<int:category_id>/<song_id>/delete', methods = ['GET', 'POST'])
def deleteSong(category_id, song_id):
    category = session.query(Category).filter(Category.id == category_id).one()
    songToDelete = session.query(Song).filter(Song.id == song_id).one()
    if request.method == 'POST':
        session.delete(songToDelete)
        session.commit()
        return redirect(url_for('showCategorySongs', category = category.name, category_id = category_id))
    else:
        return render_template('deletesong.html', song = songToDelete, category = category)

@app.route('/categories/<category>/<int:category_id>/newsong', methods = ['GET', 'POST'])
def newSong(category, category_id):
    if request.method == 'POST':
        newSong = Song(name = request.form['name'],
                       key = request.form['key'],
                       year = request.form['year'],
                       composer = request.form['composer'],
                       bpm = request.form['bpm'],
                       timesig = request.form['timesig'],
                       source = request.form['source'],
                       category_id = category_id)
        session.add(newSong)
        session.commit()
        return redirect(url_for('showCategorySongs', category = category, category_id = category_id))
    else:
        return render_template('newsong.html', category = category, category_id = category_id)

#results = session.query(Tags.tags, Tags.song_id).filter(Tags.tags.like('%hungarian%')).all()
#print results

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
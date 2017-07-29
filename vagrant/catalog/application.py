#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 12:58:48 2017

@author: markhorvath
"""
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response
from functools import wraps

from songsdb_setup import Base, Category, Song, User

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///songs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Flask Login Decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Route to login


@app.route('/login/')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.
                                  digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Route to connect via Google


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Valitdate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check for valid access_token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if not add user to db
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: \
                150px;-webkit-border-radius: 150px;\
                -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# Disconnect from Google, remove user's login session and token


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect from session


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        # removed fbdisconnect for now, will add fb connectivity later,
        # fbdisconnect should go here

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in.")
        return redirect(url_for('showCategories'))

# Route to main page


@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).group_by(Category.name).all()
    for i in categories:
        i.name = i.name.title()
        songsInCategory = session.query(func.count(Song.name)).filter(
            Song.category_id == i.id).all()
        i.count = int(songsInCategory[0][0])

    if 'username' not in login_session:
        return render_template('publiccategories.html', categories=categories)
    else:
        return render_template('categories.html', categories=categories)

# Route to specific category songs


@app.route('/categories/<path:category>/<int:category_id>')
def showCategorySongs(category, category_id):
    songs = session.query(Song).filter(Song.category_id == category_id).all()

    if 'username' not in login_session:
        return render_template('publicsongs.html', songs=songs,
                               category=category,
                               category_id=category_id)
    else:
        return render_template('categorysongs.html', songs=songs,
                               category=category,
                               category_id=category_id)


@app.route('/about/')
def showAbout():
    return render_template('about.html')

# Routes to get JSON APIS for Categories and Songs


@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/categories/<int:category_id>/JSON')
def categorySongsJSON(category_id):
    songs = session.query(Song).filter(Song.category_id == category_id).all()
    return jsonify(category_songs=[c.serialize for c in songs])


@app.route('/categories/<int:category_id>/song/<int:song_id>/JSON')
def songJSON(category_id, song_id):
    songInfo = session.query(Song).filter(Song.id == song_id).one()
    return jsonify(songInfo=songInfo.serialize)

# Route to song details


@app.route('/categories/<path:category>/<int:category_id>/<name>/\
           <int:song_id>')
def showSongInfo(category, category_id, song_id, name):
    song = session.query(Song).filter(Song.id == song_id).one()
    return render_template('songinfo.html', song=song, name=name)

# Route to add a new category


@app.route('/category/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash('New Category %s Successfully Created' % newCategory.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')

# Route to edit a category


@app.route('/category/<path:category>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category):
    editedCategory = session.query(Category).filter(
        Category.name.like(category)).one()
    oldName = editedCategory.name
    if editedCategory.user_id == login_session['user_id']:
        if request.method == 'POST':
            if request.form['name']:
                editedCategory.name = request.form['name']
                flash('Category %s Successfully Changed to %s' %
                      (oldName, editedCategory.name))
                return redirect(url_for('showCategories'))
        else:
            return render_template('editcategory.html',
                                   category=editedCategory)
    else:
        flash('You may only edit categories you created!')
        return redirect(url_for('showCategories'))

# Route to edit a song


@app.route('/category/<path:category>/<int:song_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editSong(category, song_id):
    category = category.title()
    currentCategory = session.query(Category).filter(
                      Category.name == category).one()
    editedSong = session.query(Song).filter(Song.id == song_id).one()
    if editedSong.user_id == login_session['user_id']:
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
            return redirect(url_for('showCategorySongs',
                                    category=currentCategory.name,
                                    category_id=currentCategory.id))
        else:
            return render_template('editsong.html', category=category,
                                   song=editedSong,
                                   song_id=editedSong.id)
    else:
        flash('You may only edit songs you created!')
        return redirect(url_for('showCategorySongs',
                                category=currentCategory.name,
                                category_id=currentCategory.id))

# Route to delete a category


@app.route('/categories/<path:category>/<int:category_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteCategory(category, category_id):
    categoryToDelete = session.query(Category).filter(
        Category.id == category_id).one()
    deletedName = categoryToDelete.name
    if categoryToDelete.user_id == login_session['user_id']:
        if request.method == 'POST':
            session.delete(categoryToDelete)
            session.commit()
            flash('Successfully deleted category %s' % deletedName)
            return redirect(url_for('showCategories',
                                    category_id=category_id))
        else:
            return render_template('deletecategory.html',
                                   category=categoryToDelete)
    else:
        flash('You may only delete categories you created!')
        return redirect(url_for('showCategories',
                                category_id=category_id))

# Route to delete a song


@app.route('/categories/<int:category_id>/<song_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteSong(category_id, song_id):
    category = session.query(Category).filter(Category.id == category_id).one()
    songToDelete = session.query(Song).filter(Song.id == song_id).one()
    deletedName = songToDelete.name
    if songToDelete.user_id == login_session['user_id']:
        if request.method == 'POST':
            session.delete(songToDelete)
            session.commit()
            flash('Successfully deleted song %s' % deletedName)
            return redirect(url_for('showCategorySongs',
                                    category=category.name,
                                    category_id=category_id))
        else:
            return render_template('deletesong.html',
                                   song=songToDelete, category=category)
    else:
        flash('You may only delete songs you created!')
        return redirect(url_for('showCategorySongs',
                                category=category.name,
                                category_id=category_id))


# Route to add a new song


@app.route('/categories/<path:category>/<int:category_id>/newsong',
           methods=['GET', 'POST'])
@login_required
def newSong(category, category_id):
    if request.method == 'POST':
        newSong = Song(name=request.form['name'],
                       key=request.form['key'],
                       year=request.form['year'],
                       composer=request.form['composer'],
                       bpm=request.form['bpm'],
                       timesig=request.form['timesig'],
                       category_id=category_id,
                       user_id=login_session['user_id'])
        session.add(newSong)
        session.commit()
        flash('New Song "%s" added to %s' % (newSong.name, category))
        return redirect(url_for('showCategorySongs',
                                category=category,
                                category_id=category_id))
    else:
        return render_template('newsong.html',
                               category=category,
                               category_id=category_id)


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

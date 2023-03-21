from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, LostObjects, FoundObjects
from . import db
import json
# we want to import the file logger.py
from logger import logger

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
# @login_required
def index():
    # log the gettting of the index page
    logger.debug('Getting the index page')
    return render_template("index.html")

@views.route('/home', methods=['GET', 'POST'])
# @login_required
def home():
    # log the gettting of the index page
    logger.debug('Getting the home page')
    if request.method == 'POST':
        note = request.form.get('note')
        new_note = Note(data=note, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        return render_template("home.html", user=current_user)
    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/post_loss', methods=['GET', 'POST'])
def post_loss():
    if request.method == 'POST':
        loster = current_user.email
        description = request.form.get('description')
        place = request.form.get('place')
        classifier = request.form.get('classifier')

        if len(description) < 1:
            flash('Description is too short!', category='error')
        else:
            new_lost_object = LostObjects(loster=loster, description=description, place=place, classifier=classifier)
            db.session.add(new_lost_object)
            db.session.commit()
            flash('Object added!', category='success')

    return render_template("post_loss.html", user=current_user)

# make a route to see all the lost objects
@views.route('/lost_objects', methods=['GET'])
def lost_objects():
    # query all the lost objects
    lost_objects = LostObjects.query.all()
    return render_template("lost_objects.html", user=current_user, lost_objects=lost_objects)

# make a route to delete a lost object use a route that would be like /delete-lost-object/<id>
@views.route('/delete-lost-object/<id>', methods=['GET'])
def delete_lost_object(id):
    # query the lost object with the id
    lost_object = LostObjects.query.filter_by(id=id).first()
    # delete the lost object
    db.session.delete(lost_object)
    db.session.commit()
    # kleep the user on the same page
    return redirect(url_for('views.lost_objects'))

@views.route('/post_found', methods=['GET', 'POST'])
def post_found():
    if request.method == 'POST':
        founder = current_user.email
        description = request.form.get('description')
        place = request.form.get('place')
        classifier = request.form.get('classifier')

        if len(description) < 1:
            flash('Description is too short!', category='error')
        else:
            new_found_object = FoundObjects(founder=founder, description=description, place=place, classifier=classifier)
            db.session.add(new_found_object)
            db.session.commit()
            flash('Object added!', category='success')

    return render_template("post_found.html", user=current_user)

# make a route to see all the lost objects
@views.route('/found_objects', methods=['GET'])
def found_objects():
    # query all the lost objects
    found_objects = FoundObjects.query.all()
    return render_template("found_objects.html", user=current_user, found_objects=found_objects)

# make a route to delete a lost object use a route that would be like /delete-lost-object/<id>
@views.route('/delete-found-object/<id>', methods=['GET'])
def delete_found_object(id):
    # query the lost object with the id
    found_object = FoundObjects.query.filter_by(id=id).first()
    # delete the lost object
    db.session.delete(found_object)
    db.session.commit()
    # kleep the user on the same page
    return redirect(url_for('views.found_objects'))

# make a /search-lost-objects route that would take a query string and search for the lost objects
@views.route('/search-lost-objects', methods=['GET', 'POST'])
def search_lost_objects():
    if request.method == 'POST':
        query = request.form.get('query')
        # log thre queru
        logger.debug(f'Query: {query}')
        if query:
            # log the query
            logger.debug(f'Query: {query}')
            # query the lost objects (filter the lost objects by the query: they must not necessarily be exactly the same, but as long as there are some words that are the same in the classifier or description, then it should be returned)
            lost_objects = LostObjects.query.filter(LostObjects.description.contains(query) | LostObjects.classifier.contains(query)).all()
            return render_template("lost_objects.html", user=current_user, lost_objects=lost_objects)
        else:
            # do nothing
            return redirect(url_for('views.lost_objects'))
        
# make a /search-lost-object-location route that would take a query string and search for the lost objects by location
@views.route('/search-lost-object-location', methods=['GET', 'POST'])
def search_lost_object_location():
    if request.method == 'POST':
        query = request.form.get('query')
        # log thre queru
        logger.debug(f'Query: {query}')
        if query:
            # log the query
            logger.debug(f'Query: {query}')
            # query the lost objects
            lost_objects = LostObjects.query.filter(LostObjects.place.contains(query)).all()
            return render_template("lost_objects.html", user=current_user, lost_objects=lost_objects)
        else:
            # do nothing
            return redirect(url_for('views.lost_objects'))

# make a /search-lost-object-classifier route that would take a query string and search for the lost objects by classifier
@views.route('/search-lost-object-classifier', methods=['GET', 'POST'])
def search_lost_object_classifier():
    if request.method == 'POST':
        query = request.form.get('query')
        # log thre queru
        logger.debug(f'Query: {query}')
        if query:
            # log the query
            logger.debug(f'Query: {query}')
            # query the lost objects
            lost_objects = LostObjects.query.filter(LostObjects.classifier.contains(query)).all()
            return render_template("lost_objects.html", user=current_user, lost_objects=lost_objects)
        else:
            # do nothing
            return redirect(url_for('views.lost_objects'))
        
# make a /search-lost-object-date route that would take a query string and search for the lost objects by date. We return the lost objects whose lost_date falls within the range of the query. Recall the form looks like <form method="POST" action="/search-lost-object-date" class="needs-validation" novalidate> <div class="form-group"> <label for="search">Earliest Lost Date:</label> <input type="date" name="earliest_date" class="form-control" required> <div class="invalid-feedback"> Please provide a valid name. </div> </div> <div class="form-group"> <label for="search">Latest Lost Date:</label> <input type="date" name="latest_date" class="form-control" required> <div class="invalid-feedback"> Please provide a valid name. </div> </div> <button type="submit" class="btn btn-primary">Search</button> </form>
@views.route('/search-lost-object-date', methods=['GET', 'POST'])
def search_lost_object_date():
    if request.method == 'POST':
        earliest_date = request.form.get('earliest_date')
        latest_date = request.form.get('latest_date')
        # log the query
        logger.debug(f'Earliest Date: {earliest_date}')
        logger.debug(f'Latest Date: {latest_date}')
        # query the lost objects
        lost_objects = LostObjects.query.filter(LostObjects.lost_date.between(earliest_date, latest_date)).all()
        return render_template("lost_objects.html", user=current_user, lost_objects=lost_objects)
    else:
        # do nothing
        return redirect(url_for('views.lost_objects'))
# make a /search-found-objects route that would take a query string and search for the lost objects
@views.route('/search-found-objects', methods=['GET', 'POST'])
def search_found_objects():
    if request.method == 'POST':
        query = request.form.get('query')
        # log thre queru
        logger.debug(f'Query: {query}')
        if query:
            # log the query
            logger.debug(f'Query: {query}')
            # query the lost objects
            found_objects = FoundObjects.query.filter(FoundObjects.description.contains(query)).all()
            return render_template("found_objects.html", user=current_user, found_objects=found_objects)
        else:
            # do nothing
            return redirect(url_for('views.found_objects'))
    
# make a /search-found-object-location route that would take a query string and search for the lost objects by location
@views.route('/search-found-object-location', methods=['GET', 'POST'])
def search_found_object_location():
    if request.method == 'POST':
        query = request.form.get('query')
        # log thre queru
        logger.debug(f'Query: {query}')
        if query:
            # log the query
            logger.debug(f'Query: {query}')
            # query the lost objects
            found_objects = FoundObjects.query.filter(FoundObjects.place.contains(query)).all()
            return render_template("found_objects.html", user=current_user, found_objects=found_objects)
        else:
            # do nothing
            return redirect(url_for('views.found_objects'))
        
# make a /search-found-object-classifier route that would take a query string and search for the lost objects by classifier
@views.route('/search-found-object-classifier', methods=['GET', 'POST'])
def search_found_object_classifier():
    if request.method == 'POST':
        query = request.form.get('query')
        # log thre queru
        logger.debug(f'Query: {query}')
        if query:
            # log the query
            logger.debug(f'Query: {query}')
            # query the lost objects
            found_objects = FoundObjects.query.filter(FoundObjects.classifier.contains(query)).all()
            return render_template("found_objects.html", user=current_user, found_objects=found_objects)
        else:
            # do nothing
            return redirect(url_for('views.found_objects'))
        




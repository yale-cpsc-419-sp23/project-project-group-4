from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import LostObjects, FoundObjects, People
from . import db
from datetime import datetime
import json
# We want to import the file logger.py
from logger import logger

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
# @login_required
def index():
    # Log the getting of the index page
    logger.debug('Getting the index page')
    return render_template("index.html")

@views.route('/home', methods=['GET'])
def home():
    # log the getting of the index page
    logger.debug('Getting the home page')
    # query all the lost objects
    user_lost_objects = LostObjects.query.filter(LostObjects.loster.contains(current_user.email)).all()
    lost_objects = LostObjects.query.all()
    # query all the found objects
    user_found_objects = FoundObjects.query.filter(FoundObjects.founder.contains(current_user.email)).all()
    found_objects = FoundObjects.query.all()
    
    return render_template("home.html", user=current_user, lost_objects=lost_objects, found_objects=found_objects,
                           user_lost_objects=user_lost_objects, user_found_objects=user_found_objects)

# Post lost item
@views.route('/post_loss', methods=['GET', 'POST'])
def post_loss():
    if request.method == 'POST':
        loster = current_user.email
        description = request.form.get('description')
        place = request.form.get('place')
        classifier = request.form.get('classifier')
        lost_date = request.form.get('lost_date')

        new_lost_object = LostObjects(loster=loster, description=description, place=place, classifier=classifier, lost_date=datetime.strptime(lost_date, '%Y-%m-%d'))
        db.session.add(new_lost_object)
        db.session.commit()
        flash('Object added!', category='success')
        return redirect(url_for('views.home'))

    return render_template("post_loss.html", user=current_user)

# Update database record
@views.route('/update_lost_object/<id>', methods=['GET', 'POST'])
def update_lost_object(id):
    lost_object = LostObjects.query.get_or_404(id)
    if request.method == 'POST':
        lost_object.description = request.form.get('description')
        lost_object.place = request.form.get('place')
        lost_object.classifier = request.form.get('classifier')
        lost_object.lost_date = datetime.strptime(request.form.get('lost_date'), '%Y-%m-%d')
        try:
            db.session.commit()
            flash("Updated Successfully")
            return redirect(url_for('views.home'))
        except:
            flash("Error", category='error')
            return redirect(url_for('views.home'))
    else:
        date = lost_object.lost_date.strftime('%Y-%m-%d')
        return render_template("update_loss.html", user=current_user, lost_object=lost_object, date=date)

# make a route to delete a lost object use a route that would be like /delete-lost-object/<id>
@views.route('/delete-lost-object/<id>', methods=['GET'])
def delete_lost_object(id):
    # query the lost object with the id
    lost_object = LostObjects.query.filter_by(id=id).first()
    # delete the lost object
    db.session.delete(lost_object)
    db.session.commit()
    # kleep the user on the same page
    flash('Object Deleted', category='error')
    return redirect(url_for('views.home'))

################################################################################################################################################
# Post found item
@views.route('/post_found', methods=['GET', 'POST'])
def post_found():
    if request.method == 'POST':
        founder = current_user.email
        description = request.form.get('description')
        place = request.form.get('place')
        classifier = request.form.get('classifier')
        found_date = request.form.get('found_date')

        new_found_object = FoundObjects(founder=founder, description=description, place=place, classifier=classifier, found_date=datetime.strptime(found_date, '%Y-%m-%d'))
        db.session.add(new_found_object)
        db.session.commit()
        flash('Object added!', category='success')
        return redirect(url_for('views.home'))

    return render_template("post_found.html", user=current_user)

# Update database record
@views.route('/update_found_object/<id>', methods=['GET', 'POST'])
def update_found_object(id):
    found_object = FoundObjects.query.get_or_404(id)
    if request.method == 'POST':
        found_object.description = request.form.get('description')
        found_object.place = request.form.get('place')
        found_object.classifier = request.form.get('classifier')
        found_object.found_date = datetime.strptime(request.form.get('found_date'), '%Y-%m-%d')
        try:
            db.session.commit()
            flash("Updated Successfully")
            return redirect(url_for('views.home'))
        except:
            flash("Error", category='error')
            return redirect(url_for('views.home'))
    else:
        date = found_object.found_date.strftime('%Y-%m-%d')
        return render_template("update_found.html", user=current_user, found_object=found_object, date=date)

# make a route to delete a found object use a route that would be like /delete-found-object/<id>
@views.route('/delete-found-object/<id>', methods=['GET'])
def delete_found_object(id):
    # query the found object with the id
    found_object = FoundObjects.query.filter_by(id=id).first()
    # delete the found object
    db.session.delete(found_object)
    db.session.commit()
    # kleep the user on the same page
    flash('Object Deleted', category='error')
    return redirect(url_for('views.home'))

#################################################################################################################################################
# Search objects
# make a /search-objects route that would take a query string and search for the lost objects
@views.route('/search-objects', methods=['GET', 'POST'])
def search_objects():
    if request.method == 'POST':
        query = request.form.get('query')
        # log thre queru
        logger.debug(f'Query: {query}')
        if query:
            # log the query
            logger.debug(f'Query: {query}')
            # query the lost objects (filter the lost objects by the query: they must not necessarily be exactly the same, but as long as there are some words that are the same in the classifier or description, then it should be returned)
            user_lost_objects = LostObjects.query.filter(LostObjects.loster.contains(current_user.email) & (LostObjects.description.contains(query) | LostObjects.classifier.contains(query))).all()
            lost_objects = LostObjects.query.filter(LostObjects.description.contains(query) | LostObjects.classifier.contains(query)).all()
            # query the lost objects (filter the found objects by the query: they must not necessarily be exactly the same, but as long as there are some words that are the same in the classifier or description, then it should be returned)
            user_found_objects = FoundObjects.query.filter(FoundObjects.founder.contains(current_user.email) & (FoundObjects.description.contains(query) | FoundObjects.classifier.contains(query))).all()
            found_objects = FoundObjects.query.filter(FoundObjects.description.contains(query) | FoundObjects.classifier.contains(query)).all()
            return render_template("home.html", user=current_user, lost_objects=lost_objects, found_objects=found_objects,
                           user_lost_objects=user_lost_objects, user_found_objects=user_found_objects)
        else:
            # do nothing
            return redirect(url_for('views.home'))
        
# make a /search-object-location route that would take a query string and search for the lost objects by location
@views.route('/search-object-location', methods=['GET', 'POST'])
def search_object_location():
    if request.method == 'POST':
        query = request.form.get('place')
        # log thre queru
        logger.debug(f'Place: {query}')
        if query:
            # log the query
            logger.debug(f'Place: {query}')
            # query the lost objects
            user_lost_objects = LostObjects.query.filter(LostObjects.loster.contains(current_user.email) & LostObjects.place.contains(query)).all()
            lost_objects = LostObjects.query.filter(LostObjects.place.contains(query)).all()
            # query the found objects
            user_found_objects = FoundObjects.query.filter(FoundObjects.founder.contains(current_user.email) & FoundObjects.place.contains(query)).all()
            found_objects = FoundObjects.query.filter(FoundObjects.place.contains(query)).all()
            return render_template("home.html", user=current_user, lost_objects=lost_objects, found_objects=found_objects,
                           user_lost_objects=user_lost_objects, user_found_objects=user_found_objects)
        else:
            # do nothing
            return redirect(url_for('views.home'))

# make a /search-object-classifier route that would take a query string and search for the lost objects by classifier
@views.route('/search-object-classifier', methods=['GET', 'POST'])
def search_object_classifier():
    if request.method == 'POST':
        query = request.form.get('classifier')
        # log thre queru
        logger.debug(f'Query: {query}')
        if query:
            # log the query
            logger.debug(f'Query: {query}')
            # query the lost objects
            user_lost_objects = LostObjects.query.filter(LostObjects.loster.contains(current_user.email) & LostObjects.classifier.contains(query)).all()
            lost_objects = LostObjects.query.filter(LostObjects.classifier.contains(query)).all()
            # query the found objects
            user_found_objects = FoundObjects.query.filter(FoundObjects.founder.contains(current_user.email) & FoundObjects.classifier.contains(query)).all()
            found_objects = FoundObjects.query.filter(FoundObjects.classifier.contains(query)).all()
            return render_template("home.html", user=current_user, lost_objects=lost_objects, found_objects=found_objects,
                           user_lost_objects=user_lost_objects, user_found_objects=user_found_objects)
        else:
            # do nothing
            return redirect(url_for('views.home'))
        
# make a /search-object-date route that would take a query string and search for the lost objects by date
@views.route('/search-object-date', methods=['GET', 'POST'])
def search_lost_object_date():
    if request.method == 'POST':
        date = request.form.get('lost_date')
        # log the query
        logger.debug(f'Date: {date}')
        # query the lost objects
        user_lost_objects = LostObjects.query.filter(LostObjects.loster.contains(current_user.email) & LostObjects.lost_date.contains(date)).all()
        lost_objects = LostObjects.query.filter(LostObjects.lost_date.contains(date)).all()
         # query the found objects
        user_found_objects = FoundObjects.query.filter(FoundObjects.founder.contains(current_user.email) & FoundObjects.found_date.contains(date)).all()
        found_objects = FoundObjects.query.filter(FoundObjects.found_date.contains(date)).all()
        return render_template("home.html", user=current_user, lost_objects=lost_objects, found_objects=found_objects,
                           user_lost_objects=user_lost_objects, user_found_objects=user_found_objects)
    else:
        # do nothing
        return redirect(url_for('views.home'))

@views.route('/user_info', methods=['GET'])
def user():
    # log the getting of the index page
    logger.debug('Getting the user data page')
    # get the data for this specific user
    user_data = People.query.filter(People.username.contains(current_user.email)).all()
    user_lost_objects = LostObjects.query.filter(LostObjects.loster.contains(current_user.email)).all()
    user_found_objects = FoundObjects.query.filter(FoundObjects.founder.contains(current_user.email)).all()
    #users = People.query.all()
    
    return render_template("user.html", user=current_user, user_data=user_data, user_lost_objects=user_lost_objects, user_found_objects=user_found_objects, \
                           num_lost=len(user_lost_objects), num_found=len(user_found_objects))

@views.route('/message', methods=['GET, POST'])
def message():
    raise NotImplementedError
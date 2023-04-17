from flask import Flask, render_template, request, flash, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import func, distinct, and_, or_
from .models import LostObjects, FoundObjects, People, Message
from . import db
from datetime import datetime
from flask_cas import CAS, login_required, login, logout
# We want to import the file logger.py
from logger import logger
import os
import yalies

app = Flask(__name__, template_folder='./templates')
cas = CAS(app)
api = yalies.API('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2ODE2NzExNjMsInN1YiI6ImFteTI0In0.Xg1CivwFdFtZw7h-nAM-MHmcunVEefeYsFHHKXg33J8')
app.config['CAS_SERVER'] = 'https://secure6.its.yale.edu/cas/'
app.config['CAS_AFTER_LOGIN'] = 'https://127.0.0.1:17290/'
app.config['CAS_AFTER_LOGOUT'] = 'https://127.0.0.1:17290/'
app.secret_key = 'My beautiful and long secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{"database.db"}'
app.config['SESSION_TYPE'] = 'cookie'
app.config['SESSION_PERMANENT'] = True

# Set the path for uploaded files
UPLOAD_FOLDER = os.path.join(app.root_path) + '/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

classifiers = {"Electronic": ["Laptop", "Phone", "Headphone", "Tablet", "Charger"], "Clothing": ["Shirt", "Pants", "Shoes", "Hat"], "Miscellaneous": ["Wallet", "Keys", "ID"]}
places = {"Residential College": ["Benjamin Franklin", "Pauli Murray", "Timothy Dwight", "Jonathan Edwards", "Ezra Stiles", "Morse", "Berkeley", "Saybrook", "Pierson"\
                                  , "Davenport", "Trumbull", "Silliman", "Grace Hopper", "Branford"], "Schwartzman Center": ["The Elm", "Commons", "The Well"], \
                                    "South": ["Miami"]}

with app.app_context():
    db.create_all()

#-----------------------------------------------------------------------
@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    # Log the getting of the index page
    logger.debug('Getting the index page')
    return render_template("index.html")

@app.route('/home', methods=['GET'])
@login_required
def home():
    # log the getting of the index page
    logger.debug('Getting the home page')
    # query all the lost objects
    lost_objects = LostObjects.query.all()
    # query all the found objects
    found_objects = FoundObjects.query.all()
    user = api.person(filters={'netid': cas.username})
    username = user.first_name + " " + user.last_name
    
    return render_template("home.html", user=username, lost_objects=lost_objects, found_objects=found_objects, classifiers=classifiers, places=places)

@app.route('/post', methods=['GET'])
# @login_required
def post():
    user = api.person(filters={'netid': cas.username})
    username = user.first_name + " " + user.last_name
    return render_template("post.html", user=username, classifiers=classifiers, places=places)

@app.route('/message/<id>', methods=['GET', 'POST'])
@login_required
def message(id):
    user = api.person(filters={'netid': cas.username})
    username = user.first_name + " " + user.last_name
    if request.method == 'POST':
        msg = request.form.get('message')
        new_message = Message(sender=username, receiver=id, content=msg)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('message', id=id))

    all_messages = Message.query.all()
    user_messages = Message.query.filter(Message.receiver.contains(username)).all()
    sent_messages = Message.query.filter(Message.sender.contains(username)).all()
    return render_template("message.html", user=username, send_to=id, sent_messages=sent_messages, user_messages=user_messages, all_messages=all_messages)
    
# Post lost item
@app.route('/post_loss', methods=['POST'])
@login_required
def post_loss():
    user = api.person(filters={'netid': cas.username})
    loster = user.first_name + " " + user.last_name
    description = request.form.get('description')
    place = request.form.get('place')
    classifier = request.form.get('classifier')
    lost_date = request.form.get('lost_date')

    # save the file
    file = request.files['file']
    filename = file.filename
    if filename == '':
        image = 'noimage.jpeg'
    else:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = filename

    new_lost_object = LostObjects(loster=loster, description=description, place=place, classifier=classifier, lost_date=datetime.strptime(lost_date, '%Y-%m-%d'), image=image)
    db.session.add(new_lost_object)
    db.session.commit()
    flash('Object added!', category='success')
    return redirect(url_for('home'))

# Update database record
@app.route('/update_lost_object/<id>', methods=['GET', 'POST'])
@login_required
def update_lost_object(id):
    lost_object = LostObjects.query.get_or_404(id)
    if request.method == 'POST':
        lost_object.description = request.form.get('description')
        lost_object.place = request.form.get('place')
        lost_object.classifier = request.form.get('classifier')
        lost_object.lost_date = datetime.strptime(request.form.get('lost_date'), '%Y-%m-%d')

         # save the file
        file = request.files['file']
        filename = file.filename
        if filename == '':
            image = 'noimage.jpeg'
        else:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = filename

        lost_object.image = image

        try:
            db.session.commit()
            flash("Updated Successfully")
            return redirect(url_for('user'))
        except:
            flash("Error", category='error')
            return redirect(url_for('user'))
    else:
        date = lost_object.lost_date.strftime('%Y-%m-%d')
        user = api.person(filters={'netid': cas.username})
        username = user.first_name + " " + user.last_name
        return render_template("update_loss.html", user=username, lost_object=lost_object, date=date, places=places, classifiers=classifiers)

# make a route to delete a lost object use a route that would be like /delete-lost-object/<id>
@app.route('/delete-lost-object/<id>', methods=['GET'])
@login_required
def delete_lost_object(id):
    # query the lost object with the id
    lost_object = LostObjects.query.filter_by(id=id).first()
    # delete the lost object
    db.session.delete(lost_object)
    db.session.commit()
    # kleep the user on the same page
    flash('Object Deleted', category='error')
    return redirect(url_for('user'))

################################################################################################################################################
# Post found item
@app.route('/post_found', methods=['POST'])
@login_required
def post_found():
    user = api.person(filters={'netid': cas.username})
    founder = user.first_name + " " + user.last_name
    description = request.form.get('description')
    place = request.form.get('place')
    classifier = request.form.get('classifier')
    found_date = request.form.get('found_date')

    # save the file
    file = request.files['file']
    filename = file.filename

    if filename == '':
        image = 'noimage.jpeg'
    else:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image = filename

    new_found_object = FoundObjects(founder=founder, description=description, place=place, classifier=classifier, found_date=datetime.strptime(found_date, '%Y-%m-%d'), image=image)

    db.session.add(new_found_object)
    db.session.commit()
    flash('Object added!', category='success')
    return redirect(url_for('home'))

# Update database record
@app.route('/update_found_object/<id>', methods=['GET', 'POST'])
@login_required
def update_found_object(id):
    found_object = FoundObjects.query.get_or_404(id)
    if request.method == 'POST':
        found_object.description = request.form.get('description')
        found_object.place = request.form.get('place')
        found_object.classifier = request.form.get('classifier')
        found_object.found_date = datetime.strptime(request.form.get('found_date'), '%Y-%m-%d')

         # save the file
        file = request.files['file']
        filename = file.filename
        if filename == '':
            image = 'noimage.jpeg'
        else:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = filename
        
        found_object.image = image

        try:
            db.session.commit()
            flash("Updated Successfully")
            return redirect(url_for('user'))
        except:
            flash("Error", category='error')
            return redirect(url_for('user'))
    else:
        date = found_object.found_date.strftime('%Y-%m-%d')
        user = api.person(filters={'netid': cas.username})
        username = user.first_name + " " + user.last_name
        return render_template("update_found.html", user=username, found_object=found_object, date=date, places=places, classifiers=classifiers)

# make a route to delete a found object use a route that would be like /delete-found-object/<id>
@app.route('/delete-found-object/<id>', methods=['GET'])
@login_required
def delete_found_object(id):
    # query the found object with the id
    found_object = FoundObjects.query.filter_by(id=id).first()
    # delete the found object
    db.session.delete(found_object)
    db.session.commit()
    # kleep the user on the same page
    flash('Object Deleted', category='error')
    return redirect(url_for('user'))

@app.route('/delete-message/<id>', methods=['GET'])
@login_required
def delete_message(id):
    message = Message.query.filter_by(id=id).first()
    db.session.delete(message)
    db.session.commit()
    flash('Message Deleted', category='success')
    return redirect(url_for('user'))

#################################################################################################################################################
@app.route('/search-found-objects', methods=['GET', 'POST'])
@login_required
def search_found_objects():
    if request.method == 'POST':
        query = request.args.get('query')
        place = request.args.get('place')
        classifier = request.args.get('classifier')
        date = request.args.get('lost_date')
        if not query: 
            query = '%'
        if not place:
            place = '%'
        if not classifier:
            classifier = '%'
        if not date:
            date = '%'
        
        user = api.person(filters={'netid': cas.username})
        username = user.first_name + " " + user.last_name
        
        found_objects = FoundObjects.query.filter(FoundObjects.description.contains(query) & FoundObjects.place.contains(place) & FoundObjects.classifier.contains(classifier) & FoundObjects.found_date.contains(date)).all()
        html = ""
        for found_object in found_objects:
            if found_object.founder == username: 
                html += f"""
                <div class="card my-card">
                    <div class="card-body">
                        
                        <h5 class="card-title">User: {found_object.founder}</h5>
                        <div class="card-image">
                            <img src="../static/images/{found_object.image}" alt="{found_object.description}">
                        </div>  
                        <p class="card-text">Description: {found_object.description}</p>
                        <p class="card-text">Date: {found_object.found_date}</p>
                        <!-- show the object's location on the left and the object's classifier on the right -->
                        <h6 class="card-subtitle mb-2 text-muted">Location/Classifier: {found_object.place} | {found_object.classifier}</h6>
                        <!-- show the object's omage with size of 200x200 and circle it and put it to the right of the card -->
                    
                    </div>
                </div>
                """
            else: 
                html += f"""
                <div class="card my-card">
                    <div class="card-body">
                        <div style="display: flex; justify-content: space-between;">
                            <h5 class="card-title">User: {found_object.founder}</h5>
                            <a style="margin-left: auto;" href="/message/{found_object.founder}" class="card-link">
                                <i class="fa fa-telegram" aria-hidden="true"></i>
                            </a>
                        </div>
                        <div class="card-image">
                            <img src="../static/images/{found_object.image}" alt="{found_object.description}">
                        </div>  
                        <p class="card-text">Description: {found_object.description}</p>
                        <p class="card-text">Date: {found_object.found_date}</p>
                        <!-- show the object's location on the left and the object's classifier on the right -->
                        <h6 class="card-subtitle mb-2 text-muted">Location/Classifier: {found_object.place} | {found_object.classifier}</h6>
                        <!-- show the object's omage with size of 200x200 and circle it and put it to the right of the card -->
                    </div>
                </div>
                """

        return make_response(html) 

# Search objects
# make a /search-objects route that would take a query string and search for the lost objects
@app.route('/search-lost-objects', methods=['GET', 'POST'])
@login_required
def search_lost_objects():
    if request.method == 'POST':
        query = request.args.get('query')
        place = request.args.get('place')
        classifier = request.args.get('classifier')
        date = request.args.get('lost_date')
        if not query: 
            query = '%'
        if not place:
            place = '%'
        if not classifier:
            classifier = '%'
        if not date:
            date = '%'
        
        lost_objects = LostObjects.query.filter(LostObjects.description.contains(query) & LostObjects.place.contains(place) & LostObjects.classifier.contains(classifier) & LostObjects.lost_date.contains(date)).all()
        html = ""
        user = api.person(filters={'netid': cas.username})
        username = user.first_name + " " + user.last_name
        for lost_object in lost_objects:
            if lost_object.loster == username: 
                html += f"""
                <div class="my-card card">
                    <div class="card-body">
                        <h5 class="card-title">User: {lost_object.loster}</h5>
                        <div class="card-image">
                            <img src="../static/images/{lost_object.image}" alt="{lost_object.description}">
                        </div>  
                        <p class="card-text">Description: {lost_object.description}</p>
                        <p class="card-text">Date: {lost_object.lost_date}</p>
                        <!-- show the object's location on the left and the object's classifier on the right -->
                        <h6 class="card-subtitle mb-2 text-muted">Location/Classifier: {lost_object.place} | {lost_object.classifier}</h6>
                        <!-- show the object's omage with size of 200x200 and circle it and put it to the right of the card -->
                        
                    </div>
                </div>
                """
            else: 
                html += f"""
                <div class="my-card card">
                    <div class="card-body">
                        <div style="display: flex; justify-content: space-between;">
                            <h5 class="card-title">User: {lost_object.loster}</h5>
                            <a  style="margin-left: auto;" href="/message/{lost_object.loster}" class="card-link">
                                <i class="fa fa-telegram" aria-hidden="true"></i>
                            </a>
                        </div>
                        <div class="card-image">
                            <img src="../static/images/{lost_object.image}" alt="{lost_object.description}">
                        </div>  
                        <p class="card-text">Description: {lost_object.description}</p>
                        <p class="card-text">Date: {lost_object.lost_date}</p>
                        <!-- show the object's location on the left and the object's classifier on the right -->
                        <h6 class="card-subtitle mb-2 text-muted">Location/Classifier: {lost_object.place} | {lost_object.classifier}</h6>
                        <!-- show the object's omage with size of 200x200 and circle it and put it to the right of the card -->
                    </div>
                </div>
                """
        return make_response(html)
        

@app.route('/user', methods=['GET'])
@login_required
def user():
    # log the getting of the index page
    logger.debug('Getting the user objects page')
    # get the data for this specific user
    user = api.person(filters={'netid': cas.username})
    username = user.first_name + " " + user.last_name
    userimage = user.image
    user_data = People.query.filter(People.username.contains(username)).all()
    user_lost_objects = LostObjects.query.filter(LostObjects.loster.contains(username)).all()
    user_found_objects = FoundObjects.query.filter(FoundObjects.founder.contains(username)).all()
    # get the data for this specific user
    # user_messages = Message.query.filter(Message.receiver.contains(username) | Message.sender.contains(username)).all()
    # Get the latest message for each sender-receiver pair
    user_messages = Message.query.filter(
        or_(Message.sender == username, Message.receiver == username)
    ).filter(
        Message.date == db.session.query(db.func.max(Message.date)).filter(
            and_(Message.sender == Message.sender, Message.receiver == Message.receiver)
        ).scalar()
    ).all()
    return render_template("user.html", username=username, image=userimage, user_data=user_data, user_lost_objects=user_lost_objects, user_found_objects=user_found_objects, \
                           num_lost=len(user_lost_objects), num_found=len(user_found_objects), user_messages=user_messages)

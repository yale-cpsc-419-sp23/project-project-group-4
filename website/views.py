from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, LostObjects
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    return render_template("index.html")



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
            new_lost_object = LostObjects(loster=loster, description=description, place_id=place, classifier_id=classifier)
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

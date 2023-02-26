from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, LostObjects
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

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
            new_lost_object = LostObjects(loster=loster, description=description, place_id=place, classifier_id=classifier)
            db.session.add(new_lost_object)
            db.session.commit()
            flash('Object added!', category='success')

    return render_template("post_loss.html", user=current_user)
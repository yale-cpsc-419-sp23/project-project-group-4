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

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class PostLossForm(FlaskForm):
    loster = StringField('Lost by', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    place = SelectField('Place', coerce=int, validators=[DataRequired()])
    classifier = SelectField('Classifier', coerce=int, validators=[DataRequired()])


@views.route('/post-loss', methods=['GET', 'POST'])
def post_loss():
    form = PostLossForm()
    if form.validate_on_submit():
        lost_object = LostObjects(
            loster=form.loster.data,
            description=form.description.data,
            place_id=form.place.data,
            classifier_id=form.classifier.data
        )
        db.session.add(lost_object)
        db.session.commit()
        flash('Lost item posted successfully!', 'success')
        # return redirect(url_for('views.home')) 
    return render_template('post_loss.html', form=form)

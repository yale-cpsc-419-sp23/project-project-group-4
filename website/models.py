from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class People(db.Model):
    __tablename__ = 'people'
    username = db.Column(db.String(100), primary_key=True)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    num_lost_items = db.Column(db.Integer, default=0)
    num_found_items = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)

class Places(db.Model):
    __tablename__ = 'places'
    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(100), unique=True)

class Classifier(db.Model):
    __tablename__ = 'classifier'
    id = db.Column(db.Integer, primary_key=True)
    classifier_name = db.Column(db.String(100), unique=True)

class LostObjects(db.Model):
    __tablename__ = 'lost_objects'
    id = db.Column(db.Integer, primary_key=True)
    loster = db.Column(db.String(100), db.ForeignKey('people.username'))
    description = db.Column(db.String(1000))
    lost_date = db.Column(db.DateTime, default=datetime.utcnow)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'))
    classifier_id = db.Column(db.Integer, db.ForeignKey('classifier.id'))

class FoundObjects(db.Model):
    __tablename__ = 'found_objects'
    id = db.Column(db.Integer, primary_key=True)
    founder = db.Column(db.String(100), db.ForeignKey('people.username'))
    name = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    found_date = db.Column(db.DateTime, default=datetime.utcnow)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'))
    classifier_id = db.Column(db.Integer, db.ForeignKey('classifier.id'))


class Note(db.Model): # TO BE DELETED
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    lost_id = db.Column(db.Integer, db.ForeignKey('lost_objects.id'))
    found_id = db.Column(db.Integer, db.ForeignKey('found_objects.id'))

class User(db.Model): # TO BE DELETED
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

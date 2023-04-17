from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy



class People(db.Model):
    __tablename__ = 'people'
    username = db.Column(db.String(100), primary_key=True) 
    joined_date = db.Column(db.Date, default=datetime.utcnow().date())
    num_lost_items = db.Column(db.Integer, default=0)
    num_found_items = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)

class Message(db.Model): 
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    receiver = db.Column(db.String(100), db.ForeignKey('people.username'))
    sender = db.Column(db.String(100), db.ForeignKey('people.username'))
    content = db.Column(db.String(500))
    date = db.Column(db.DateTime, default=datetime.utcnow)

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
    lost_date = db.Column(db.Date, default=datetime.utcnow().date())
    # place_id = db.Column(db.Integer, db.ForeignKey('places.id'))
    place = db.Column(db.String(100))
    # classifier_id = db.Column(db.Integer, db.ForeignKey('classifier.id'))
    classifier = db.Column(db.String(100))
    image = db.Column(db.String(1000))

class FoundObjects(db.Model):
    __tablename__ = 'found_objects'
    id = db.Column(db.Integer, primary_key=True)
    founder = db.Column(db.String(100), db.ForeignKey('people.username'))
    name = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    found_date = db.Column(db.Date, default=datetime.utcnow().date())
    # place_id = db.Column(db.Integer, db.ForeignKey('places.id'))
    place = db.Column(db.String(100))
    # classifier_id = db.Column(db.Integer, db.ForeignKey('classifier.id'))
    classifier = db.Column(db.String(100))
    image = db.Column(db.String(1000))

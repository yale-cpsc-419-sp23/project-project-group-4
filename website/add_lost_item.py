from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from models import LostObjects

db = SQLAlchemy()
DB_NAME = "database.db"

@app.route('/lost_objects', methods=['GET'])
def get_lost():
    lost_objects = LostObjects.query.all()
    return lost_objects

@app.route('/lost_objects', methods=['POST'])
def create_lost(loster, description, lost_date, place_id, classifier_id):
    new_lost_object = LostObjects(loster=loster, description=description, lost_date=lost_date, place_id=place_id, classifier_id=classifier_id)

    db.session.add(new_lost_object)
    db.session.commit()

    return new_lost_object

@app.route('/lost_objects/<int:id>', methods=['DELETE'])
def delete_lost(id):
    lost_object = LostObjects.query.get_or_404(id)
    db.session.delete(lost_object)
    db.session.commit()

    return {'message': f'Lost object with ID {id} was successfully deleted.'}

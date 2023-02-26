from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from models import LostObjects

db = SQLAlchemy()
DB_NAME = "database.db"

@app.route('/lost_objects', methods=['GET'])
def get_lost(id):
    lost = LostObjects.query.get_or_404(id)
    return lost

@app.route('/lost_objects', methods=['POST'])
def create_lost(loster, description, lost_date, place_id, classifier_id):
    new_lost = LostObjects(loster=loster, description=description, lost_date=lost_date, place_id=place_id, classifier_id=classifier_id)

    db.session.add(new_lost)
    db.session.commit()

    return new_lost

@app.route('/lost_objects/<int:id>', methods=['DELETE'])
def delete_lost(id):
    lost_object = LostObjects.query.get_or_404(id)
    db.session.delete(lost_object)
    db.session.commit()
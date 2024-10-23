from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    salt = db.Column(db.String(50), unique = True, nullable = False)
    hashpass = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(50), unique = True)
    created_at = db.Column(db.DateTime, default = datetime.now)
    updated_at = db.Column(db.DateTime, onupdate = datetime.now)
    image_keys = db.relationship('ImageKey', backref = 'user', lazy = True)

    def __repr__(self):
        return '<User %r>' %self.username

class ImageKey(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_key = db.Column(db.String(50), unique = True)
    added_at = db.Column(db.DateTime, default = datetime.now)
    updated_at = db.Column(db.DateTime, onupdate = datetime.now)

    def __repr__(self):
        return '<ImageKey %r>' %self.id

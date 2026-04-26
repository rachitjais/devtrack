from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))

class APILog(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    endpoint=db.Column(db.String(200))
    response_time=db.Column(db.Integer)
    status=db.Column(db.Integer)
    user_id=db.Column(db.Integer)
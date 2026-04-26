from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))

class APILog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(200))
    response_time = db.Column(db.Integer)
    status = db.Column(db.Integer)
    project_id = db.Column(db.Integer)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    api_key = db.Column(db.String(200), unique=True)
    user_id = db.Column(db.Integer)
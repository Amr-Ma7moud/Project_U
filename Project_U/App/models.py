from App import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    website = db.Column(db.String(100), nullable=False, unique=True)
    university_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.Integer, nullable=False, unique=True)
    fees = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    programs = db.Column(db.String(200), nullable=False)
    min_score = db.Column(db.Integer, nullable=True)
    world_ranking = db.Column(db.Integer, nullable=True, unique=True)
    abbreviations = db.Column(db.String(100), nullable=True, unique=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    fees = db.Column(db.Integer, nullable=True)

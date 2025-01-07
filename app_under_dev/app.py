from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from tokenize import String
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (
    DataRequired,
    Length,
    ValidationError,
    Email,
    Regexp,
    EqualTo,
)
import os

# from API import Config
from flask_login import (
    LoginManager,
    UserMixin,
    logout_user,
    current_user,
    login_user,
    login_required,
)
import csv
from sqlalchemy.exc import IntegrityError
import requests
from sqlalchemy import or_
import logging
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pandas as pd

import csv
from sqlalchemy.exc import IntegrityError
import os


app = Flask(__name__)
app.config["SECRET_KEY"] = "b1zklfghapfhasefljhnwefklashndfklw"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'project_u.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "Login"


def insert_universities_from_csv(file_path):
    with open(file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            try:
                university = University(
                    name=row["name"],
                    website=row["website"],
                    university_type=row["type"],
                    location=row["location"],
                    rank=int(
                        row["rank"]
                    ),  # rank parsed correctly as int using local methods for this
                    fees=int(
                        row["fees"]
                    ),  # type casting added, if data exists that follows that
                    description=row.get("description", ""),
                    programs=row["programs"],
                    min_score=int(
                        row["min_score"]
                    ),  # parsed to integers , before value is passed
                    world_ranking=int(
                        row["world_ranking"]
                    ),  # world ranking integer, add check before insert from python to validation format . before table data entry, same method can extended other types of input check that needs be done on user end or form field . UI method use that same techniques too . for "format based  data input check
                    abbreviations=row[
                        "abbreviations"
                    ],  # unique string that mostly used  UI or view tag  properties / attributes values for dom handling and/ or also UI framework local implementations. these local ids are unique as HTML id also be that specific strings by their html component names
                )
                db.session.add(university)
                db.session.commit()
                print(f"Added university: {row['name']}")
            except IntegrityError:
                db.session.rollback()
                print(f"Skipping duplicate entry: {row['name']}")
            except (
                ValueError
            ) as ve:  # catches specific type of parsing/ cast method errors for all number format values at server/ db level operations that has invalid numerical strings
                print(
                    f"Error parsing data , number / type problem found for {row['name']},and skip  due to  Error: {ve}, try updating data on CSV using integer range etc , check string types that you intended  / value validations at server db before save methods are applied! "
                )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        search_query = request.form.get("search")
        universities = University.query.filter(
            University.name.like(f"%{search_query}%")
        ).all()
        return render_template("home.html", universities=universities)
    return render_template("home.html", universities=[])


@app.route("/aboutUs")
def aboutUs():
    return render_template("aboutUs.html")


@app.route("/compare", methods=["GET", "POST"])
def compare():
    form = Compare()
    university_ids = (form.uni1.data, form.uni2.data, form.uni3.data)
    if form.validate_on_submit():
        university_ids = [form.uni1.data, form.uni2.data, form.uni3.data]
        if len(university_ids) < 2:
            flash("Please select at least two universities to compare.", "warning")
            return redirect(url_for("compare"))

        if len(set(university_ids)) != len(university_ids):
            flash("Please select different universities to compare.", "info ")
            return redirect(url_for("compare"))

        universities = University.query.filter(University.id.in_(university_ids)).all()

        if not universities:
            flash("No universities found for the given IDs.", "danger")
            return redirect(url_for("compare"))

        return render_template("compare.html", universities=universities)

    universities = University.query.all()
    return render_template("compare.html", universities=universities, form=form)


@app.route("/Signup", methods=["GET", "POST"])
def Signup():
    if current_user.is_authenticated:
        flash("You are already loged in.", "info")
        return redirect(url_for("main"))

    form = RegistrationForm()
    if form.validate_on_submit():
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        email = form.email.data
        name = form.name.data
        username = form.username.data
        score = form.score.data
        section = form.section.data
        location = form.location.data
        fees = form.fees.data if form.fees.data else None  # Optional field

        user = User(
            email=email,
            username=username,
            section=section,
            score=score,
            password=hashed_password,
            name=name,
            location=location,
            fees = fees
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while committing to the database.", "danger")
        login_user(user)
        flash("You have signed up successfully.", "success")
        session["user_id"] = user.id
        session["user_name"] = user.name
        return redirect(url_for("main"))
    return render_template("Signup.html", form=form)


@app.route("/Login", methods=["GET", "POST"])
def Login():
    if current_user.is_authenticated:
        flash("You are already loged in.", "info")
        return redirect(url_for("main"))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=form.remember.data)
            flash("You have loged in successfully.", "success")
            session["user_id"] = user.id
            session["user_name"] = user.name
            return redirect(url_for("main"))
        flash("Invalid email or password please check credentials.", "danger")
        return redirect(url_for("Login"))
    return render_template("Login.html", form=form)


@app.route("/logout")
def logout():
    if not current_user.is_authenticated:
        flash("YOU SHOULDN'T BE THERE", "danger")
        return redirect(url_for("Login"))
    logout_user()
    flash("You loged out successfully", "info")
    return redirect(url_for("index"))


@app.route("/profile")
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for("Signup"))
    user_id = session["user_id"]
    user = User.query.get(user_id)
    return render_template("profile.html", user=user)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("search_query")  # Get user input
    results = []
    if query:
        # Perform a case-insensitive search
        results = University.query.filter(University.name.ilike(f"%{query}%")).all()
        results += University.query.filter(
            University.location.ilike(f"%{query}%")
        ).all()
        results += University.query.filter(
            University.programs.ilike(f"%{query}%")
        ).all()
        results += University.query.filter(University.website.ilike(f"%{query}%")).all()

    return render_template("home.html", results=results, query=query)


@app.route("/delete_profile", methods=["POST", "GET"])
@login_required
def delete_profile():
    user_id = session["user_id"]
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash("Your profile has been deleted.", "success")
        return redirect(url_for("index"))
    flash("User not found.", "danger")
    return redirect(url_for("profile"))


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if not current_user.is_authenticated:
        flash("You need to log in first", "info")
        return redirect(url_for("Login"))

    # Fetch the logged-in user's data
    user = User.query.get(session["user_id"])
    user_score = user.score
    user_location = (
        user.location.lower()
    )  # Normalize location for case-insensitive comparison
    user_budget = user.fees  # User's budget (can be None or 0 if not provided)
    user_section = (
        user.section.lower()
    )  # User's preferred section (e.g., Engineering, Medicine)

    try:
        # Fetch all universities from the database
        universities = University.query.all()

        # Filter universities based on user preferences
        recommendations = []
        for uni in universities:
            # Calculate a match score for each university
            match_score = 0

            # Match location (case-insensitive)
            if user_location in uni.location.lower():
                match_score += 1

            # Match score (if user score >= university's min_score)
            if user_score >= uni.min_score:
                match_score += 1

            # Match fees (if user provides a budget and university fees <= user's budget)
            if user_budget and uni.fees <= user_budget:
                match_score += 1

            # Match section (if user's section is in university's programs)
            if user_section in uni.programs.lower():
                match_score += 1

            # Add the university to recommendations if it matches at least one criterion
            if match_score > 0:
                recommendations.append(
                    {
                        "name": uni.name,
                        "location": uni.location,
                        "programs": uni.programs,
                        "tuition_fee": uni.fees,
                        "website": uni.website,
                        "match_score": match_score,
                    }
                )

        # Sort recommendations by match score (highest first)
        recommendations = sorted(
            recommendations, key=lambda x: x["match_score"], reverse=True
        )

        # Limit to top 5 recommendations
        recommendations = recommendations[:5]

        # Render the recommendations on the same page
        return render_template(
            "recommend.html", recommendations=recommendations, user=user
        )

    except Exception as e:
        return render_template("recommend.html", error=str(e))


class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(100), nullable=False)
    university_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    fees = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    programs = db.Column(db.String(200), nullable=False)
    min_score = db.Column(db.Integer, nullable=True)
    world_ranking = db.Column(db.Integer, nullable=True)
    abbreviations = db.Column(db.String(100), nullable=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    fees = db.Column(db.Integer, nullable=True)

class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=25)])
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=25)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,32}$"
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    score = StringField("Score", validators=[DataRequired()])
    section = StringField("Section", validators=[DataRequired()])
    location = StringField("location", validators=[DataRequired()])
    submit = SubmitField("Sign Up")
    fees = StringField("Fees")


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already exists")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exists")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
        ],
    )
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class Compare(FlaskForm):
    uni1 = StringField("University 1", validators=[DataRequired()])
    uni2 = StringField("University 2", validators=[DataRequired()])
    uni3 = StringField("University 3")
    submit = SubmitField("Compare")


if __name__ == "__main__":
    csv_file_path = os.path.join(os.path.dirname(__file__), "code.csv")
    # with app.app_context():
        # db.create_all()
        # insert_universities_from_csv(csv_file_path)
        # insert_universities_from_csv(csv_file_path)
    app.run(debug=True, port=9000)

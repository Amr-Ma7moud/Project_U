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
# app.config.from_object(Config)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# def insert_universities_from_csv(file_path):
#     with open(file_path, mode="r", encoding="utf-8") as file:
#         csv_reader = csv.DictReader(file)
#         for row in csv_reader:
#             university = University(
#                 name=row["Name"],
#                 website=row["Website"],
#                 university_type=row["Type"],
#                 location=row["Location"],
#                 rank=int(row["Rank"]),
#                 fees=int(row["Tuition fees"]),
#                 description=row.get("description", ""),
#                 programs=row["programs"],
#             )
#             db.session.add(university)
#             try:
#                 db.session.commit()
#             except IntegrityError:
#                 db.session.rollback()
#                 print(f"Skipping duplicate entry: {row['Name']}")


@app.route("/")
@app.route("/index")
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


@app.route("/compare")
def compare():
    return render_template("compare.html")


@app.route("/recommend")
def recommend():
    if not current_user.is_authenticated:
        flash("You need to log in.", "info")
        return redirect(url_for("Signup"))
    return render_template("recommend.html")


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
        user = User(
            email=email,
            username=username,
            section=section,
            score=score,
            password=hashed_password,
            name=name,
            location=location,
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully", "success")
        return redirect(url_for("Login"))
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
        return redirect(url_for("profile"))
    return render_template("Login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/profile")
def profile():
    if current_user.is_authenticated == False:
        # if "user_id" not in session:
        return redirect(url_for("Signup"))
    user_id = session["user_id"]
    user = User.query.get(user_id)
    return render_template("profile.html", user=user)


@app.route("/search", methods=["GET", "POST"])
def search():
    name = request.args.get("search_query", "").lower()
    location = request.args.get("location", "").lower()
    tuition_fee = request.args.get("tuition_fee")
    programs = request.args.get("programs", "").lower()

    # Build the query dynamically
    query = University.query
    if name:
        query = query.filter(University.name.ilike(f"%{name}%"))
    if location:
        query = query.filter(University.location.ilike(f"%{location}%"))
    if tuition_fee:
        try:
            tuition_fee = float(tuition_fee)
            query = query.filter(University.fees <= tuition_fee)
        except ValueError:
            return jsonify({"message": "Invalid tuition fee value"}), 400
    if programs:
        query = query.filter(University.programs.ilike(f"%{programs}%"))

    universities = query.all()

    # Format the response
    result = [
        {
            "id": uni.id,
            "name": uni.name,
            "location": uni.location,
            "tuition_fee": uni.fees,
            "programs": uni.programs,
            "website": uni.website,
            "type": uni.university_type,
            "description": uni.description,
        }
        for uni in universities
    ]

    return jsonify(result)


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if not current_user.is_authenticated:
        return redirect(url_for("Login"))
    user_id = session["user_id"]
    user = User.query.get(user_id)
    return render_template("edit_profile.html", user=user)


@app.route("/delete_profile", methods=["GET", "POST"])
def delete_profile():
    if not current_user.is_authenticated:
        return redirect(url_for("Login"))
    user_id = session["user_id"]
    user = User.query.get(user_id)
    return render_template("delete_profile.html", user=user)


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


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)


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


if __name__ == "__main__":
    # csv_file_path = os.path.join(os.path.dirname(__file__), "code.csv")
    # with app.app_context():
    #     db.create_all()
    #     insert_universities_from_csv(csv_file_path)
    app.run(debug=True, port=9000)

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


def nothing():
    # just to the wrap comments
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
    pass


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


@app.route("/compare")
def compare():
    return render_template("compare.html")


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
    user_section = user.section.lower()
    user_location = user.location.lower()

    try:
        # Fetch all universities from the database
        universities = University.query.all()

        # Convert universities to a DataFrame
        data = {
            "name": [uni.name for uni in universities],
            "location": [uni.location for uni in universities],
            "programs": [uni.programs for uni in universities],
            "tuition_fee": [uni.fees for uni in universities],
            "website": [uni.website for uni in universities],
        }
        df = pd.DataFrame(data)

        # Handle missing values in `tuition_fee`
        df["tuition_fee"] = df["tuition_fee"].fillna(0)  # Replace NaN with 0

        # Handle unseen labels in 'location' and 'programs'
        unique_locations = df["location"].unique().tolist()
        unique_programs = df["programs"].unique().tolist()

        # If user_location is not in the dataset, use a default value
        if user_location not in unique_locations:
            user_location = unique_locations[0]  # Use the first location as default

        # If user_section is not in the dataset, use a default value
        if user_section not in unique_programs:
            user_section = unique_programs[0]  # Use the first program as default

        # Encode categorical features
        le_location = LabelEncoder()
        le_programs = LabelEncoder()
        df["location_encoded"] = le_location.fit_transform(df["location"])
        df["programs_encoded"] = le_programs.fit_transform(df["programs"])

        X = df[["location_encoded", "programs_encoded"]]
        y = df["tuition_fee"]  # Use tuition_fee as the target for classification

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(X_scaled, y)

        user_location_encoded = le_location.transform([user_location])[0]
        user_programs_encoded = le_programs.transform([user_section])[0]
        user_features = scaler.transform(
            [[user_location_encoded, user_programs_encoded]]
        )

        predicted_tuition_fee = knn.predict(user_features)[0]

        location_filtered = df[df["location"].str.lower() == user_location]

        if len(location_filtered) == 0:
            location_filtered = df  # Fallback to all universities
        recommendations = location_filtered[
            location_filtered["tuition_fee"] <= predicted_tuition_fee
        ]
        recommendations = recommendations.sort_values(by="tuition_fee").head(5)
        recommendations = recommendations.to_dict(orient="records")

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

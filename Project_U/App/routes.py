from App.models import University, User
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from App.form import RegistrationForm, LoginForm, Compare
from flask_login import (
    logout_user,
    current_user,
    login_user,
    login_required,
)
from App import app, db, bcrypt, login_manager
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from sqlite3 import IntegrityError
from sqlalchemy.exc import IntegrityError


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
            fees=fees,
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
        results = University.query.filter(
            University.abbreviations.ilike(f"%{query}%")
        ).all()
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

    user = User.query.get(session["user_id"])
    user_score = user.score
    user_location = user.location.lower()
    user_budget = user.fees
    user_section = user.section.lower()

    try:
        universities = University.query.all()
        recommendations = []

        for uni in universities:
            match_score = 0

            if user_location in uni.location.lower():
                match_score += 1

            if user_score >= uni.min_score:
                match_score += 1

            if user_budget and uni.fees <= user_budget:
                match_score += 1

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
        recommendations = recommendations[:5]

        return render_template(
            "recommend.html", recommendations=recommendations, user=user
        )

    except Exception as e:
        return render_template("recommend.html", error=str(e))

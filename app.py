"""Blogly application."""

import os

from flask import Flask, redirect, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_blog')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)


@app.get("/")
def display_home():
    """Redirect to list of users."""
    return redirect("/users")


@app.get("/users")
def list_users():
    """Show all users."""

    users = User.query.all()

    return render_template("users.html", users=users)


@app.get("/users/new")
def show_add_form():
    """Show an add form for users."""

    return render_template("new_user_form.html")


@app.post("/users/new")
def add_user():
    """Process the add form, adding a new user and going back to /users."""

    first_name = request.form['fname']
    last_name = request.form['lname']
    image_url = request.form['imgurl'] if request.form['imgurl'] else None

    new_user = User(first_name=first_name,
                    last_name=last_name, image_url=image_url)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.get("/users/<int:user_id>")
def show_user_detail(user_id):
    """Show information about the given user."""

    user = User.query.get_or_404(user_id)

    return render_template("user_detail.html", user=user)


@app.get("/users/<int:user_id>/edit")
def show_edit_form(user_id):
    """Show the edit page for a user."""

    user = User.query.get_or_404(user_id)

    return render_template("edit_user_form.html", user=user)


@app.post("/users/<int:user_id>/edit")
def edit_user(user_id):
    """Process the edit form, returning the user to the /users page."""

    user = User.query.get(user_id)
    print("user", user)

    user.first_name = request.form['fname'] or user.first_name
    user.last_name = request.form['lname'] or user.last_name
    user.image_url = request.form['imgurl'] or user.image_url

    db.session.commit()

    return redirect("/users")


@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """Delete the user."""

    user = User.query.get(user_id)
    print("user", user)
    user.query.delete()

    db.session.commit()

    return redirect("/users")

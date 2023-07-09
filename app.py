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
    image_url = request.form['imgurl']

    new_user = User(first_name=first_name,
                    last_name=last_name, image_url=image_url)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")

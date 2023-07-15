"""Blogly application."""

import os

from flask import Flask, redirect, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag
from sqlalchemy import desc

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
    """Displays 5 most recent posts. """

    top_five_posts = Post.query.order_by(desc('created_at')).limit(5)

    return render_template("posts/homepage.html", posts=top_five_posts)


############################# Users #############################################

@app.get("/users")
def list_users():
    """Show all users."""

    users = User.query.order_by(User.last_name, User.first_name).all()

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

    print("user-id", user.id)
    print("posts-in-user-detail", user.posts)

    return render_template("user_detail.html", user=user, posts=user.posts)


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
    db.session.delete(user)

    # User.query.filter(User.id == user_id).delete()
    db.session.commit()

    return redirect("/users")


############################# Posts #############################################

@app.get("/users/<int:user_id>/posts/new")
def show_new_post_form(user_id):
    """Show form to add a post for that user."""

    user = User.query.get_or_404(user_id)
    posts = user.posts

    return render_template('posts/new_post.html', user=user, posts=posts)


@app.post("/users/<int:user_id>/posts/new")
def handle_new_post(user_id):
    """Handle add form; add post and redirect to the user detail page."""

    # title = request['title']
    # content = request['content']

    new_post = Post(title=request.form['title'],
                    content=request.form['content'], user_id=user_id)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f"/users/{user_id}")


@app.get("/posts/<int:post_id>")
def show_post(post_id):
    """Shows a post and shows edit/delete buttons. """

    post = Post.query.get_or_404(post_id)

    return render_template('posts/post_detail.html', post=post)


@app.get("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """Show form to edit a post, and to cancel back to user page."""

    post = Post.query.get_or_404(post_id)

    return render_template('posts/post_edit.html', post=post)


@app.post("/posts/<int:post_id>/edit")
def handle_edit_post(post_id):
    """Handle editing of a post. Redirect back to the post view."""

    post = Post.query.get_or_404(post_id)

    post.title = request.form['title']
    post.content = request.form['content']

    db.session.commit()

    return redirect(f"/posts/{post_id}")


@app.post("/posts/<int:post_id>/delete")
def delete_post(post_id):
    """Delete the post."""

    post = Post.query.get_or_404(post_id)
    user_id = post.user_id

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{user_id}")


############################# Tags #############################################

@app.get("/tags")
def list_tags():
    """Lists all tags. """

    tags = Tag.query.all()

    return render_template('tags/all.html', tags=tags)


@app.get("/tags/new")
def show_new_tag_form():
    """Show form for a new tag."""

    return render_template('tags/new.html')


@app.post("/tags/new")
def handle_new_tag():
    """Process add form, adds tag, and redirect to tag list."""

    tag = Tag(name=request.form['name'])

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")


@app.get("/tags/<int:tag_id>")
def show_tag_detail(tag_id):
    """Show detail about a tag. """

    tag = Tag.query.get_or_404(tag_id)
    posts = tag.posts

    return render_template('tags/detail.html', tag=tag, posts=posts)


@app.get("/tags/<int:tag_id>/edit")
def show_edit_tag_form(tag_id):
    """Show form to edit a tag. """

    tag = Tag.query.get_or_404(tag_id)

    return render_template('tags/edit.html', tag=tag)


@app.post("/tags/<int:tag_id>/edit")
def handle_edit_tag(tag_id):
    """Handle tag edit. Redirect to tag list. """

    tag = Tag.query.get_or_404(tag_id)

    tag.name = request.form['name']

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")


@app.post("/tags/<int:tag_id>/delete")
def delete_tag(tag_id):
    """Delete a tag."""

    tag = Tag.query.get_or_404(tag_id)

    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")

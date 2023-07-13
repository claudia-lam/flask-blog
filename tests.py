from models import DEFAULT_IMAGE_URL, User, Post
from app import app, db
from unittest import TestCase
import os

os.environ["DATABASE_URL"] = "postgresql:///blogly_test"


# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        Post.query.delete()
        User.query.delete()

        self.client = app.test_client()

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )

        db.session.add(test_user)
        db.session.commit()

        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id
        # print("test-1-user-id", self.user_id)

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_users(self):
        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)

    def test_show_add_form(self):
        with self.client as c:
            resp = c.get("/users/new")
            self.assertEqual(resp.status_code, 200)
            html = resp.text
            self.assertIn("""<label for="fname">""", html)
            self.assertIn("""<label for="lname">""", html)

    def test_add_user(self):
        with self.client as c:
            resp = c.post("/users/new", data={
                'fname': "test2_first",
                'lname': "test2_last",
                'imgurl': "",
            }, follow_redirects=True)
            html = resp.text

            # test if it is in the database
            new_user = User.query.filter(
                User.first_name == "test2_first").one_or_none()
            self.assertTrue(new_user)

            # test if we are redirecting to /users
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<li>test2_first test2_last</li>", html)

    def test_show_user_detail(self):
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>test1_first test1_last</h1>", html)

    def test_show_edit_form(self):
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}/edit")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("""<input type="text" id="fname" name="fname" value="test1_first"><br>
""", html)

    def test_edit_user(self):
        with self.client as c:
            resp = c.post(f"/users/{self.user_id}/edit", data={
                'fname': "test1_first_updated",
                'lname': "test1_last",
                'imgurl': DEFAULT_IMAGE_URL
            }, follow_redirects=True)

            # check if first name is updated
            user = User.query.get(self.user_id)
            self.assertEqual(user.first_name, "test1_first_updated")

    def test_delete_user(self):
        with self.client as c:
            resp = c.post(f"/users/{self.user_id}/delete")

            user = User.query.get(self.user_id)
            self.assertEqual(user, None)
            self.assertEqual(resp.status_code, 302)

######################### POSTS ################################################


class PostViewTestCase(TestCase):
    """Test views for posts"""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        Post.query.delete()
        User.query.delete()

        self.client = app.test_client()

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )

        db.session.add(test_user)
        db.session.commit()

        self.user_id = test_user.id

        test_post = Post(
            title="test1_title",
            content="test1_content",
            created_at=None,
            user_id=self.user_id
        )

        db.session.add(test_post)
        db.session.commit()

        # print("test-user", test_user.id)

        # We can hold onto our test_post's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.post_id = test_post.id
        print("outer-post-id", self.post_id)
        print("self-user-id", self.user_id)

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_show_new_post_form(self):
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}/posts/new")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1_first", html)
            self.assertIn("Add", html)

    def test_handle_new_post(self):
        with self.client as c:
            resp = c.post(f"/users/{self.user_id}/posts/new", data={
                'title': "A new post title",
                'content': "some new content"
            }, follow_redirects=True)

            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<li>A new post title</li>', html)

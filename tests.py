from models import DEFAULT_IMAGE_URL, User, Post, Tag, PostTag
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
        PostTag.query.delete()
        Tag.query.delete()
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
        PostTag.query.delete()
        Tag.query.delete()
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
            self.assertIn(
                '<input type="submit" id="add" value="Add Post">', html)

    def test_show_post(self):
        with self.client as c:
            resp = c.get(f"/posts/{self.post_id}")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>test1_title</h1>', html)
            self.assertIn('<p>By test1_first test1_last</p>', html)
            self.assertIn('Edit', html)
            self.assertIn('Delete', html)

    def test_edit_post(self):
        with self.client as c:
            resp = c.get(f"/posts/{self.post_id}/edit")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1_title", html)
            self.assertIn("test1_content", html)
            self.assertIn("Cancel", html)
            self.assertIn("Edit", html)

    def test_handle_edit_post(self):
        with self.client as c:
            resp = c.post(f"/posts/{self.post_id}/edit", data={
                "title": "test1_title_edited",
                "content": "test1_content_edited"
            }, follow_redirects=True)

            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1_title_edited", html)
            self.assertIn("test1_content_edited", html)

    def test_delete_post(self):
        with self.client as c:
            resp = c.post(f"/posts/{self.post_id}/delete",
                          follow_redirects=True)

            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("test1_title", html)


######################### TAGS ################################################

class TagViewTestCase(TestCase):
    """Test views for tags"""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.

        PostTag.query.delete()
        Tag.query.delete()
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

        # We can hold onto our test_post's id
        self.post_id = test_post.id

        test_tag = Tag(
            name="test_tag_1"
        )
        test_tag_2 = Tag(
            name="test_tag_2"
        )
        test_tag_3 = Tag(
            name="test_tag_3"
        )

        db.session.add_all([test_tag, test_tag_2, test_tag_3])
        db.session.commit()

        self.tag_id = test_tag.id
        self.tag_2_id = test_tag_2.id
        self.tag_3_id = test_tag_3.id

        test_post_tag = PostTag(
            post_id=self.post_id,
            tag_id=self.tag_id
        )
        test_post_tag_2 = PostTag(
            post_id=self.post_id,
            tag_id=self.tag_2_id
        )

        db.session.add_all([test_post_tag, test_post_tag_2])
        db.session.commit()

        print("outer-post-id", self.post_id)
        print("self-user-id", self.user_id)

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_tags(self):

        with self.client as c:
            resp = c.get("/tags")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<li>test_tag_1</li>', html)
            self.assertIn('Add Tag', html)

    def test_show_new_tag_form(self):
        with self.client as c:
            resp = c.get("/tags/new")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create a Tag', html)

    def test_handle_new_tag(self):
        with self.client as c:
            resp = c.post("/tags/new", data={
                'name': 'test_new_tag'
            }, follow_redirects=True)

            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test_new_tag", html)

    def test_show_tag_detail(self):
        with self.client as c:
            resp = c.get(f"/tags/{self.tag_id}")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test_tag_1", html)
            # check if related post is rendered
            self.assertIn("test1_title", html)

    def test_show_edit_tag_form(self):
        with self.client as c:
            resp = c.get(f"/tags/{self.tag_id}/edit")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit a Tag", html)

    def test_handle_edit_tag(self):
        with self.client as c:
            resp = c.post(f"/tags/{self.tag_id}/edit", data={
                'name': 'an updated tag'
            }, follow_redirects=True)

            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn('an updated tag', html)
            self.assertNotIn('test_tag_1', html)

    def test_delete_tag(self):
        with self.client as c:
            resp = c.post(f"/tags/{self.tag_id}/delete", follow_redirects=True)
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('test_tag_1', html)

    def test_show_new_post_form_with_tags(self):
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}/posts/new")
            html = resp.text

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test_tag_1", html)
            self.assertIn("test_tag_2", html)
            self.assertIn("test_tag_3", html)

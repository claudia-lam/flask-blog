from app import app
from models import db, User

db.drop_all()
db.create_all()

user_no_image = User(
    first_name="Claudia",
    last_name="lam",
)

user_with_image = User(
    first_name="Jane",
    last_name="Doe",
    image_url="https://m.media-amazon.com/images/M/MV5BMTM3OTUwMDYwNl5BMl5BanBnXkFtZTcwNTUyNzc3Nw@@._V1_FMjpg_UX1000_.jpg"
)

db.session.add_all([user_no_image, user_with_image])
db.session.commit()

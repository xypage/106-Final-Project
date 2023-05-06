###################################################
#                     Imports                     #
###################################################
# Generic imports
from sys import stdout
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    session,
    jsonify,
    render_template_string,
)
from datetime import datetime, timedelta

# Database
from flask_sqlalchemy import SQLAlchemy

# Login
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)


# For the session secret key
from os import urandom

app = Flask(__name__)
# Set a secret_key to use session/login_manager
app.secret_key = urandom(12)
# Setup bcrypt to hash passwords
bcrypt = Bcrypt(app)
# Setup the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# Admin
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
admin = Admin(app, name="Admin View", template_mode="bootstrap3")


@login_manager.user_loader
def load_user(user_id):
    # p("load_user user_id: ", user_id)
    return User.query.filter_by(id=user_id).first()


##################################################
#               Debugging functions              #
##################################################


def p(*kwargs):
    print(kwargs, file=stdout)


##################################################
#                 Database Setup                 #
##################################################
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///forum_db.sqlite"
# To avoid the "FSADeprecationWarning"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Association table for who the user is following
follows = db.Table(
    "follows",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
)
# Association table for posts the user likes
likes = db.Table(
    "likes",
    db.Column("liker_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
)
attending = db.Table(
    "attending",
    db.Column("attending_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("event_id", db.Integer, db.ForeignKey("event.id")),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # usernames should be unique, but names aren't necessarily
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    # Role is either teacher or student
    role = db.Column(db.String, nullable=False)
    # Password is the hashed version of the user's password
    password = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)
    # Posts is a list of all the posts the user has made
    posts = db.relationship("Post", backref="user")
    # Follows is a list of all the users the user is following
    followed = db.relationship(
        "User",
        secondary=follows,
        primaryjoin=(follows.c.follower_id == id),
        secondaryjoin=(follows.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )
    liked = db.relationship(
        "Post",
        secondary=likes,
        primaryjoin=(likes.c.liker_id == id),
        secondaryjoin=(likes.c.post_id == id),
        backref=db.backref("likes", lazy="dynamic"),
        lazy="dynamic",
    )
    # attending_events = db.relationship(
    #     "Event",
    #     secondary=attending,
    #     primaryjoin=(attending.c.attending_id == id),
    #     secondaryjoin=(attending.c.event_id == id),
    #     backref=db.backref("attending", lazy="dynamic"),
    # )

    def __init__(self, username, name, password, role):
        self.username = username
        self.name = name
        self.password = bcrypt.generate_password_hash(password)
        self.role = role
        self.bio = "This user hasn't created their bio yet!"

    def check_password(self, password):
        # p("Passwords:", self.password, bcrypt.generate_password_hash(password))
        return bcrypt.check_password_hash(self.password, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id is the id of the user who made the post (foreign key)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # content is the content of the post
    content = db.Column(db.String, nullable=False)
    # timestamp is the time the post was made
    timestamp = db.Column(db.DateTime, nullable=False)
    # privacy_setting is the privacy setting of the post
    privacy_setting = db.Column(db.String, nullable=False)
    comments = db.relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.String)
    parent_post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    parent_post = db.relationship("Post", back_populates="comments")


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id is the id of the user hosting the event (foreign key)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # Title is the name of the event
    title = db.Column(db.String, nullable=False)
    # description is the description of the event
    description = db.Column(db.String, nullable=False)
    # timestamp is the time the event was posted
    timestamp = db.Column(db.DateTime, nullable=False)
    # event time is when the event is happening
    event_time = db.Column(db.DateTime, nullable=False)
    # attendees = db.relationship(
    #     "User", secondary=attending, backref=db.backref("attending", lazy="dynamic")
    # )
    attendees = db.relationship(
        "User",
        secondary=attending,
        # primaryjoin=(attending.c.attending_id == db.ForeignKey("user.id")),
        # secondaryjoin=(attending.c.event_id == id),
        # backref=db.backref("attending", lazy="dynamic"),
    )


from random import randint


def load_data():
    # Make a bunch of names/passwords
    users = [
        ["Xavier", "xypage", "password"],
        ["Adam", "adam", "password"],
        ["Bob", "bob", "password"],
        ["Charlie", "charlie", "password"],
        ["Dylan", "dylan", "password"],
        ["Emily", "emily", "password"],
        ["Frank", "frank", "password"],
        ["George", "george", "password"],
        ["Harry", "harry", "password"],
        ["Isabelle", "isabelle", "password"],
        ["John", "john", "password"],
        ["Katy", "katy", "password"],
    ]
    # Load some filler text we can use for the bios
    with open("lorem.txt", "r") as lorem_file:
        lorem_text = lorem_file.read().split(".")

    with app.app_context():
        # Create all the users
        for i in range(len(users)):
            new_user = User(users[i][1], users[i][0], users[i][2], "user")
            # Set their bios to random parts of the filler text
            lorem_index = randint(0, len(lorem_text) - 5)
            new_user.bio = ".".join(lorem_text[lorem_index : lorem_index + 5]) + "."
            db.session.add(new_user)
            db.session.commit()
            # Replace the user in the list (just an array) with the user's id
            users[i] = new_user.id

        # Iterate through all the users, following random other users and making random posts
        for user_id in users:
            user = User.query.get(user_id)
            # Decide how many they should each follow, between 1 and the number of users - 1
            num_to_follow = randint(1, len(users) - 1)
            followed = 0
            while followed < num_to_follow:
                # Pick a user to follow
                user_to_follow = User.query.get(users[randint(0, len(users) - 1)])
                # Only add them if it isn't the current user
                if user_to_follow.id != user.id and user_to_follow not in user.followed:
                    user.followed.append(user_to_follow)
                    db.session.commit()
                    followed += 1

            for post_num in range(randint(1, 5)):
                post_length = randint(1, 5)
                lorem_index = randint(0, len(lorem_text) - post_length)
                post_text = (
                    ".".join(lorem_text[lorem_index : lorem_index + post_length]) + "."
                )

                # Create a new post object
                # Get the current time and subtract a random amount of time from it,
                # that way all the posts don't say they were made at the same time
                post_time = datetime.now() - timedelta(
                    days=randint(0, 30),
                    hours=randint(0, 24),
                    minutes=randint(0, 60),
                    seconds=randint(0, 60),
                )
                new_post = Post(
                    user_id=user.id,
                    content=post_text,
                    timestamp=post_time,
                    privacy_setting="public",
                )
                db.session.add(new_post)
                db.session.commit()

            event_length = randint(1, 5)
            lorem_index = randint(0, len(lorem_text) - event_length)
            event_text = (
                ".".join(lorem_text[lorem_index : lorem_index + event_length]) + "."
            )
            event_time = datetime.now() + timedelta(
                # From -30 to 30, so events can have passed already
                days=randint(-30, 30),
                hours=randint(0, 24),
                minutes=randint(0, 60),
                seconds=randint(0, 60),
            )
            user_event = Event(
                user_id=user_id,
                title=user.name + "'s Event",
                description=event_text,
                event_time=event_time,
                timestamp=datetime.now(),
            )
            db.session.add(user_event)
            db.session.commit()

        # Iterate through again so they can attend events, needs to be a separate loop because events need to have been created already
        for user_id in users:
            user = User.query.get(user_id)
            other_user_id = user_id
            while other_user_id == user_id:
                other_user_id = users[randint(0, len(users) - 1)]
            other_user_event = Event.query.filter_by(user_id=other_user_id).first()
            other_user_event.attendees.append(user)
            db.session.commit()


with app.app_context():
    pass
    # db.drop_all()
    # db.create_all()
    # load_data()


###################################################
#         Event Management (User View)            #
###################################################
@app.route("/unattend/<int:event_id>", methods=["POST"])
@login_required
def unattend(event_id):
    event = Event.query.get(event_id)
    event.attendees.remove(current_user)
    db.session.commit()
    return "Successfully unattended"

@app.route("/attend/<int:event_id>", methods=["POST"])
@login_required
def attend(event_id):
    event = Event.query.get(event_id)
    event.attendees.append(current_user)
    db.session.commit()
    return "Successfully attended"

@app.route("/load_events")
@login_required
def load_events():
    all_events = (
        Event.query.filter(Event.event_time > datetime.now())
        .order_by(Event.event_time.asc())
        .all()
    )
    event_list = []
    for event in all_events:
        event_poster = User.query.get(event.user_id)
        event_dict = {
            "event_id": event.id,
            "title": event.title,
            "description": event.description,
            "timestamp": event.timestamp,
            "event_time": event.event_time,
            "poster_id": event.user_id,
            "poster_name": event_poster.name,
            "poster_username": event_poster.username,
            "attending": current_user in event.attendees,
            "from_current": current_user.id == event.user_id
        }
        event_list.append(event_dict)
    return render_template("event_list.html", event_list=event_list)

@app.route("/attending_events")
@login_required
def attending_events():
    all_events = (
        Event.query.filter(Event.event_time > datetime.now())
        .order_by(Event.event_time.asc())
        .all()
    )
    event_list = []
    for event in all_events:
        if(current_user in event.attendees):
            event_poster = User.query.get(event.user_id)
            event_dict = {
                "event_id": event.id,
                "title": event.title,
                "description": event.description,
                "timestamp": event.timestamp,
                "event_time": event.event_time,
                "poster_id": event.user_id,
                "poster_name": event_poster.name,
                "poster_username": event_poster.username,
                "attending": current_user in event.attendees,
                "from_current": current_user.id == event.user_id
            }
            event_list.append(event_dict)
    return render_template("event_list.html", event_list=event_list)

@app.route("/new_event", methods=["POST"])
@login_required
def new_event():
    data = request.get_json()
    p(data)
    user_event = Event(
        user_id=current_user.id,
        title=data["title"],
        description=data["description"],
        event_time=datetime.fromisoformat(data["date"]),
        timestamp=datetime.now(),
    )
    db.session.add(user_event)
    db.session.commit()
    return "a"

@app.route("/delete_event/<int:event_id>", methods=["DELETE"])
@login_required
def delete_event(event_id):
    event = Event.query.get(event_id)
    if(event != None and event.user_id == current_user.id):
        db.session.delete(event)
        db.session.commit()
        return "Successfully removed"
    return "Failed to remove"

##################################################
#         Post Management (User View)            #
##################################################


@app.route("/new_post", methods=["POST"])
@login_required
def new_post():
    # Get the post data from the form
    print("in new post route")
    content = request.form["content"]

    # Create a new post object
    new_post = Post(
        user_id=current_user.id,
        content=content,
        timestamp=datetime.now(),
        privacy_setting="public",
    )
    db.session.add(new_post)
    db.session.commit()

    all_posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_data = []

    for post in all_posts:
        user = User.query.filter_by(id=post.user_id).first()
        post_data = {
            "content": post.content,
            "timestamp": post.timestamp,
            "username": user.username,
            "name": user.name,
        }
        posts_data.append(post_data)

    return jsonify(posts_data)

    # Render the new post HTML and return it
    # post_html = render_template_string('<div> class="post"><p>{{ content}}</p><p>{{ timestamp }}</p></div>', content=content, timestamp=new_post.timestamp)
    # return jsonify(post_html)


# endpoint to get all posts from the database (global feed)
@app.route("/get_all_posts", methods=["GET"])
@login_required
def get_all_posts():
    all_posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_data = []

    for post in all_posts:
        user = User.query.filter_by(id=post.user_id).first()
        post_data = {
            "content": post.content,
            "timestamp": post.timestamp,
            "username": user.username,
            "name": user.name,
            "id": post.id,
        }
        posts_data.append(post_data)

    return jsonify(posts_data)


# endpoint to get the posts of who the user is following (following feed)
@app.route("/get_following_posts", methods=["GET"])
@login_required
def get_following_posts():
    # get the unique ids of the people the current user is following
    following_ids = [user.id for user in current_user.followed]
    # A users own posts should show up in their feed as well
    following_ids.append(current_user.id)
    # get all the posts form the following ids
    following_posts = (
        Post.query.filter(Post.user_id.in_(following_ids))
        .order_by(Post.timestamp.desc())
        .all()
    )
    post_list = []
    for post in following_posts:
        user = User.query.filter_by(id=post.user_id).first()
        post_data = {
            "content": post.content,
            "timestamp": post.timestamp,
            "username": user.username,
            "name": user.name,
        }
        post_list.append(post_data)
    return jsonify(post_list)


@app.route("/user/posts/<string:username>")
def get_users_posts(username):
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    users_posts = (
        Post.query.filter_by(user_id=user_id).order_by(Post.timestamp.desc()).all()
    )
    post_list = []
    for post in users_posts:
        post_data = {
            "content": post.content,
            "timestamp": post.timestamp,
            "username": user.username,
            "name": user.name,
        }
        post_list.append(post_data)
    return jsonify(post_list)


##################################################
#         User Info Management (User View)       #
##################################################


@app.route("/get_current_user_name", methods=["Get"])
@login_required
def get_current_user_name():
    print(current_user.name)
    return current_user.name


@app.route("/get_current_user_posts", methods=["GET"])
@login_required
def get_current_user_posts():
    current_user_posts = (
        Post.query.filter_by(user_id=current_user.id)
        .order_by(Post.timestamp.desc())
        .all()
    )
    post_list = []
    for post in current_user_posts:
        post_data = {
            "content": post.content,
            "timestamp": post.timestamp,
            "username": current_user.username,
            "name": current_user.name,
        }
        post_list.append(post_data)

    print(post_list)
    return jsonify(post_list)


@app.route("/edit_bio", methods=["POST"])
@login_required
def edit_bio():
    current_user.bio = request.get_json()["new_bio"]
    db.session.commit()
    return "Bio successfully updated", 200


@app.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    post_to_like = Post.query.get(post_id)
    if post_to_like is not None:
        current_user.liked.append(post_to_like)
        db.session.commit()
        return "Post successfully liked", 200
    else:
        return "Post not found", 404


##################################################
#         Follow Management (User View)          #
##################################################
# route for follow request
@app.route("/follow_user/<int:user_id>", methods=["POST"])
@login_required
def follow_user(user_id):
    user_to_follow = User.query.get(user_id)
    # check to make sure user exists
    if user_to_follow is not None:
        if user_to_follow not in current_user.followed:
            current_user.followed.append(user_to_follow)
            db.session.commit()
            return "Successfully followed user", 200
        else:
            return "Already following user", 200
    return "User to follow is not found", 404


# route to get list of users that that the current user is following
@app.route("/user/<string:username>/following", methods=["GET"])
@login_required
def get_followed_users(username):
    followed_users = User.query.filter_by(username=username).first().followed
    user_data = [
        {"id": user.id, "username": user.username, "name": user.name}
        for user in followed_users
    ]
    return jsonify(user_data)


@app.route("/user/<string:username>/followed_by", methods=["GET"])
@login_required
def get_followers(username):
    followers = User.query.filter_by(username=username).first().followers
    user_data = [
        {"id": user.id, "username": user.username, "name": user.name}
        for user in followers
    ]
    return jsonify(user_data)


# route for unfollow request
@app.route("/unfollow_user/<int:user_id>", methods=["POST"])
@login_required
def unfollow_user(user_id):
    user_to_unfollow = User.query.get(user_id)
    # check to make sure user exists
    if user_to_unfollow is not None:
        # remove the user to be unfollowed from the association table
        current_user.followed.remove(user_to_unfollow)
        # update database
        db.session.commit()
        return "Successfully unfollowed user", 200
    return "User to unfollow is not found", 404


# route for removing a follower from the current user
@app.route("/remove_follower/<int:user_id>", methods=["POST"])
@login_required
def remove_follower(user_id):
    user_to_make_unfollow = User.query.get(user_id)
    # check to make sure user exists
    if user_to_make_unfollow is not None:
        # remove the user to be unfollowed from the association table
        user_to_make_unfollow.followed.remove(current_user)
        # update database
        db.session.commit()
        return "Successfully unfollowed user", 200
    return "User to unfollow is not found", 404


##################################################
#                Login Management                #
##################################################


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Render login page
        return render_template("login.html")
    elif request.method == "POST":
        # This is the path for if they're posting a login request, so we want to
        # process that and send them to the right place after
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        user = User.query.filter_by(username=request.form["username"]).first()
        # p("User before login", user)
        # p("Password", request.form["password"])
        if user is None or not user.check_password(request.form["password"]):
            return redirect(url_for("login"))

        login_user(user, remember=True)
        return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # Render register page
        return render_template("register.html")
    elif request.method == "POST":
        # Make new user using data in request.form
        new_user = User(
            request.form["username"],
            request.form["name"],
            request.form["password"],
            "user",
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for("home"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


####################################################
#              Main route definitions              #
####################################################
# Just to avoid the favicon error, favicon.ico is an empty file
@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.ico"))


@app.route("/")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    else:
        return render_template("home.html", user=current_user)


@app.route("/aboutUs")
def about():
    return render_template("aboutUs.html")


@app.route("/events")
@login_required
def events():
    all_events = (
        Event.query.filter(Event.event_time > datetime.now())
        .order_by(Event.event_time.asc())
        .all()
    )
    event_list = []
    for event in all_events:
        event_poster = User.query.get(event.user_id)
        event_dict = {
            "event_id": event.id,
            "title": event.title,
            "description": event.description,
            "timestamp": event.timestamp,
            "event_time": event.event_time,
            "poster_id": event.user_id,
            "poster_name": event_poster.name,
            "poster_username": event_poster.username,
            "attending": current_user in event.attendees,
            "from_current": current_user.id == event.user_id
        }
        event_list.append(event_dict)
    return render_template("events.html", event_list=event_list)


@app.route("/profile/")
@login_required
def viewProfile():
    # return render_template("profile.html")
    return redirect("/user/" + current_user.username)


@app.route("/user/<string:username>")
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    # get all the posts from this user
    users_posts = (
        Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    )
    post_list = []
    for post in users_posts:
        post_data = {"content": post.content, "timestamp": post.timestamp}
        post_list.append(post_data)

    user = {
        "name": user.name,
        "username": user.username,
        "user_id": user.id,
        "followed": current_user.is_authenticated and user in current_user.followed,
        "bio": user.bio,
        "is_current": current_user.is_authenticated
        and current_user.username == username,
    }
    return render_template("test_profile.html", post_list=post_list, user=user)



if __name__ == "__main__":
    app.run(debug=True)

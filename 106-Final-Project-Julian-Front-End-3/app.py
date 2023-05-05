###################################################
#                     Imports                     #
###################################################
# Generic imports
from sys import stdout
# from flask_admin.contrib.sqla import ModelView
# from flask_admin import Admin
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, render_template_string
from datetime import datetime

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
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
# admin = Admin(app, name='Admin View', template_mode='bootstrap3')


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
    'follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
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
    posts = db.relationship('Post', backref='user')
    # Follows is a list of all the users the user is following
    followed = db.relationship(
        'User', secondary=follows,
        primaryjoin=(follows.c.follower_id==id),
        secondaryjoin=(follows.c.followed_id==id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # user_id is the id of the user who made the post (foreign key)
    content = db.Column(db.String, nullable=False)
    # content is the content of the post
    timestamp = db.Column(db.DateTime, nullable=False)
    # timestamp is the time the post was made
    privacy_setting = db.Column(db.String, nullable=False)
    # privacy_setting is the privacy setting of the post

with app.app_context():
    # db.drop_all()
    db.create_all()

##################################################
#         Post Management (User View)            #
##################################################

@app.route("/new_post", methods=["GET", "POST"])
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
        privacy_setting="public"
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
@app.route('/get_all_posts', methods=["GET"])
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
        }
        posts_data.append(post_data)

    return jsonify(posts_data)

# endpoint to get the posts of who the user is following (following feed)
@app.route('/get_following_posts', methods=["GET"])
@login_required
def get_following_posts():
    # get the unique ids of the people the current user is following
    following_ids = [user.id for user in current_user.followed]
    # get all the posts form the following ids
    following_posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.timestamp.desc()).all()
    post_list = []
    for post in following_posts:
        user = User.query.filter_by(id=post.user_id).first()
        post_data ={
            "content": post.content,
            "timestamp": post.timestamp,
            "username": user.username,
            "name": user.name,
        }
        post_list.append(post_data)
    return jsonify(post_list)


@app.route("/user/posts/<string:username>")
def get_users_posts(username):
    user =  User.query.filter_by(username=username).first()
    user_id = user.id
    users_posts = Post.query.filter_by(user_id=user_id).order_by(Post.timestamp.desc()).all()
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

@app.route('/get_current_user_name', methods=["Get"])
@login_required
def get_current_user_name():
    print(current_user.name)
    return current_user.name

@app.route('/get_current_user_posts', methods=["GET"])
@login_required
def get_current_user_posts():
    current_user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).all()
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



##################################################
#         Follow Management (User View)          #
##################################################

# route to get list of users that the current user is not following
@app.route('/get_unfollowed_users', methods=["GET"])
@login_required
def get_unfollowed_users():
    followed_user_ids = [user.id for user in current_user.followed]
    unfollowed_users = User.query.filter(User.id.notin_(followed_user_ids + [current_user.id])).all()
    user_data = [{"id": user.id, "username": user.username, "name": user.name} for user in unfollowed_users]
    return jsonify(user_data)

# route for follow request
@app.route('/follow_user/<int:user_id>', methods=["POST"])
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
@app.route('/get_followed_users', methods=["GET"])
@login_required
def get_followed_users():
    followed_users_id = [user.id for user in current_user.followed]
    followed_users = User.query.filter(User.id.in_(followed_users_id)).all()
    user_data = [{"id": user.id, "username": user.username, "name": user.name} for user in followed_users]
    return jsonify(user_data)
    

#route for unfollow request
@app.route('/unfollow_user/<int:user_id>', methods=["POST"])
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
            request.form["username"], request.form["name"], request.form["password"], "user")
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
def events():
    return render_template("events.html")

@app.route("/profile/")
@login_required
def viewProfile():
    return render_template("profile.html")

@app.route("/user/<string:username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    # get all the posts from this user
    users_posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    post_list = []
    for post in users_posts:
        post_data = {
            "content": post.content,
            "timestamp": post.timestamp
        }
        post_list.append(post_data)

    user = {
        "name": user.name,
        "username": user.username, 
        "user_id": user.id,
        "followed": current_user.is_authenticated and user in current_user.followed,
        "bio": user.bio
    }
    # Check if the profile is the profile of the current user
    is_user = current_user.is_authenticated and current_user.username == username
    return render_template("test_profile.html", post_list=post_list, user=user, is_user=is_user)



if __name__ == "__main__":
    app.run(debug=True)

    

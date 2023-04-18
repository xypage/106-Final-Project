###################################################
#                     Imports                     #
###################################################
# Generic imports
from sys import stdout
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask import Flask, render_template, request, url_for, redirect, session

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
admin = Admin(app, name='Admin View', template_mode='bootstrap3')


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


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    # usernames should be unique, but names aren't necessarily
    name = db.Column(db.String, nullable=False)
    # Role is either teacher or student
    role = db.Column(db.String, nullable=False)
    # Password is the hashed version of the user's password
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, name, password, role):
        self.username = username
        self.name = name
        self.password = bcrypt.generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        # p("Passwords:", self.password, bcrypt.generate_password_hash(password))
        return bcrypt.check_password_hash(self.password, password)


with app.app_context():
    db.drop_all()
    db.create_all()

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
        new_user = User(request.form["username"],request.form["name"], request.form["password"],"user")
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
    elif current_user.role == "admin":
        return redirect("/admin")
    else:
        return render_template("home.html", user=current_user)






if __name__ == "__main__":
    app.run(debug=True)
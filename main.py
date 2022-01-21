from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import date

import os.path

print(os.getcwd())
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(BASE_DIR, ".db")
# with sqlite3.connect(db_path) as db:

app = Flask(__name__)

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

li = []

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
# Line below only required once, when creating DB.


# db.create_all()


@app.route('/')
def home():
    today = date.today()
    return render_template("index.html", logged_in=current_user.is_authenticated, today=today)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':

        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        # login and authenticate user after adding details to the database
        login_user(new_user)

        return render_template("secrets.html", name=new_user.name)

    return render_template("register.html", logged_in=current_user.is_authenticated)


# read last email id from the User database
# mails = User.query.with_entities(User.name).all()
# print(mails[-1])
# mails = User.query.filter(User.email.endswith('@gmail.com')).all()
# print(mails[-1])
# d = User.query.get(mails[-1])
# print(d)
# results = User.query.filter_by('email').order_by(sqlalchemy.desc(User.email)).all() #.first() #.all() #order_by(sqlalchemy.desc(Valuation.date)).all()
# first_valuation = results[0]
# last_mail = results[-1]
# user = User.query.filter_by(email=email).first()
# obj = db.session.query(User).order_by(User.id.desc()).first()
# print(obj)

# create a new database for the authenticated user by its email id.
# print(last_mail)
# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{mails[-1]}.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db2 = SQLAlchemy(app)
#
# # TODO: CREATE A NEW TABLE IN THE SAME DATABASE TO ADD TODAY'S TO-DOS TO IT.
# # Today = date.today()
# class Today(db2.Model):
#     id = db2.Column(db2.Integer, primary_key=True)
#     status = db2.Column(db2.String(10), default="False")
#     task = db2.Column(db2.String(100))


# db2.create_all()
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(BASE_DIR, f"{mails[-1]}.db")
# with sqlite3.connect(db_path) as db:


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # find user by email entered
        user = User.query.filter_by(email=email).first()

        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        # Email exists and password correct
        else:
            login_user(user)
            return render_template('secrets.html', name=user.name)

    return render_template("login.html", logged_in=current_user.is_authenticated)


# to get all the mail ids
mails = User.query.with_entities(User.name).all()

class Today(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # status = db.Column(db.String(10), default="False")
    task = db.Column(db.String(100))


# db.create_all()

# mails = User.query.with_entities(User.name).all()
# print(mails[-1])
# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{mails[-1]}.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db2 = SQLAlchemy(app)
#
# # TODO: CREATE A NEW TABLE IN THE SAME DATABASE TO ADD TODAY'S TO-DOS TO IT.
# # Today = date.today()
# class Today(db2.Model):
#     id = db2.Column(db2.Integer, primary_key=True)
#     status = db2.Column(db2.String(10), default="False")
#     task = db2.Column(db2.String(100))


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
def download():
    return send_from_directory(
        directory='static', filename='files/cheat_sheet.pdf'
    )


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        new_task = Today(
            task=request.form.get('task')
        )

        db.session.add(new_task)
        db.session.commit()

    return render_template("add_task.html")


if __name__ == "__main__":
    app.run(debug=True)

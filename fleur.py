#!/usr/bin/env python3
import datetime
import locale
import sqlite3
import json

from flask_wtf import Form
from wtforms import BooleanField, PasswordField, SubmitField, TextField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import ValidationError
from flask_login import LoginManager
from flask import (
    Flask,
    g,
    render_template,
    request, redirect,
)



login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)


DATABASE = 'guestBook.db'


class LoginForm(Form):
    email = TextField('Email',
            validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        # user = User.query.filter_by(email=self.email.data).first()
        user = None
        if not user:
            self.email.errors.append('Unknown email')
            return False
        if not user.verify_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False
        return True
    
    
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, *args):
    db = get_db()
    cur = db.execute(query, args)
    if query.lower().startswith('select '):
        rows = cur.fetchall()
    else:
        db.commit()
        rows = []
    cur.close()
    return rows


def init():
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    query_db("""
            CREATE TABLE IF NOT EXISTS comments(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
                name VARCHAR(100),
                visit_date DATE,
                comment VARCHAR(500),
                response VARCHAR(500)
            );
        """)
    print('init execute')


@app.route('/login', methods=['POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    # if form.validate_on_submit():
    #     # Login and validate the user.
    #     # user should be an instance of your `User` class
    #     login_user(user)

    #     flask.flash('Logged in successfully.')

    #     next = flask.request.args.get('next')
    #     # url_has_allowed_host_and_scheme should check if the url is safe
    #     # for redirects, meaning it matches the request host.
    #     # See Django's url_has_allowed_host_and_scheme for an example.
    #     if not url_has_allowed_host_and_scheme(next, request.host):
    #         return flask.abort(400)

    #     return flask.redirect(next or flask.url_for('index'))
    print(request)
    return flask.render_template('login.html', form=form)


@app.route("/")
def redirect_home():
    return redirect('/home')


@app.route("/home/")
def go_home():
    return render_template('index.html')


@app.route("/guest_book/")
def add_guest_book():
    recent_comments = query_db("SELECT name, visit_date, comment FROM comments ORDER BY visit_date DESC")
    return render_template('guest_book.html', recent_comments=[
        {
            "name": row["name"],
            "visit_date": datetime.datetime.strptime(row["visit_date"], "%Y-%m-%d").strftime("%B %Y"),
            "comment": row["comment"],
        }
        for row in recent_comments
    ])


@app.route('/add_comment/', methods=["POST"])
def comment():
    query_db("INSERT INTO comments (name, visit_date, comment) VALUES(?,?,?)",
             request.form['name'],
             request.form['visit_date'],
             request.form['comment'],
             )
    return redirect('/guest_book')


@app.route('/show_comments/')
def comments():
    all_comments = query_db("SELECT name, visit_date, comment FROM comments")
    return render_template('view_comments.html', all_comments=all_comments)


@app.route('/contact/')
def contact():
    with open('static/opening_hours.json', 'r') as hours:
        data = json.load(hours)
    print(data)
    return render_template('contactezmoi.html', opening_hours=data)


@app.route('/who_i_am/')
def who_i_am():
    return render_template('who_i_am.html')


@app.route('/activities/')
def activities():
    return render_template('activities.html')


@app.route('/prices/')
def prices():
    with open('static/prices.json', 'r') as prices_json:
        data = json.load(prices_json)
    return render_template('prices.html', prices=data)


with app.app_context():
    init()

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1')

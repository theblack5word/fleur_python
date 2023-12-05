#!/usr/bin/env python3
import datetime
import locale
import sqlite3
import json

from flask_mail import Mail, Message
from flask import (
    Flask,
    g,
    render_template,
    request, redirect,
)

app = Flask(__name__)

# app.config['APPLICATION_ROOT'] = '/'

app.config.from_pyfile('../webmail_config.py')

mail = Mail(app)

DATABASE = 'guestBook.db'


# test
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


@app.route("/")
def redirect_home():
    return redirect('/home')


@app.route("/home/")
def home():
    with open('static/img_link_index.json', 'r') as imgs:
        data = json.load(imgs)
    return render_template('index.html', imgs=data)


@app.route("/guest_book/")
def guest_book():
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
def add_comment():
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
    return render_template('contactezmoi.html', opening_hours=data, toaster='false')


@app.route('/send_mail/', methods=["POST"])
def send_mail():
    object_mail = "{0} {1} cherche a joindre Fleur de sérénité. ".format(request.form['name'],
                                                                         request.form['first_name'])
    mail_body = ("Bonjour Tiffany,\n {0} {1} cherche à vous joindre, voici son message : \n \n {3} \n \n pour lui "
                 "répondre voici son adresse : {2} \n bonne journée")
    msg = Message(object_mail, sender='contact@fleurdeserenite.eu', recipients=['remi.bonnand@gmail.com'])
    msg.body = mail_body.format(
        request.form['name'],
        request.form['first_name'],
        request.form['mail'],
        request.form['content'])
    mail.send(msg)
    with open('static/opening_hours.json', 'r') as hours:
        data = json.load(hours)
    with open('static/opening_hours.json', 'r') as hours:
        data = json.load(hours)
    return render_template('contactezmoi.html', opening_hours=data, toaster='true')


@app.route('/who_i_am/')
def who_i_am():
    return render_template('who_i_am.html')


@app.route('/activities/')
def activities():
    with open('static/img_link.json', 'r') as img_link:
        data = json.load(img_link)
    return render_template('activities.html', img_link=data)


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

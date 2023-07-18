#!/usr/bin/env python3
import datetime
import locale
import sqlite3


from flask import (
    Flask,
    g,
    render_template,
    request, redirect,
)

app = Flask(__name__)

DATABASE = 'guestBook.db'


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


with app.app_context():
    init()

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1')

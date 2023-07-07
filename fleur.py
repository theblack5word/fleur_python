#!/usr/bin/env python3
import sqlite3

from flask import (
    Flask,
    g,
    render_template,
    request, redirect,
)
from mpmath import fib

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


def verif_and_add_table():
    """check if comments table exist, and create it if no exist."""
    query_db("""
            CREATE TABLE IF NOT EXISTS comments(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
                name VARCHAR(100),
                visitDate DATE,
                comment VARCHAR(500)
            );
        """)


@app.route("/")
def go_home():
    return render_template('index.html')


@app.route("/guest_book")
def add_guest_book():
    recent_comments = query_db("SELECT name, visitDate, comment FROM comments LIMIT 4")
    return render_template('guest_book.html', comments=recent_comments)


@app.route('/add_comment/', methods=["POST"])
def comment():
    verif_and_add_table()
    query_db("INSERT INTO comments VALUES(NULL,?,?,?)",
             request.form['name'],
             request.form['visitDate'],
             request.form['comment'],
             )
    return redirect('/guest_book')


@app.route('/show_comments/')
def comments():
    verif_and_add_table()
    all_comments = query_db("SELECT name, visitDate, comment FROM comments")
    return render_template('view_comments.html', comments=all_comments)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='127.0.0.1')

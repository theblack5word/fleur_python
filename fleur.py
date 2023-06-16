#!/usr/bin/env python3
import sqlite3

from flask import (
    Flask,
    g,
    render_template,
    request,
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
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows


# @app.route("/")
# def hello_world():
#     all_comments = query_db("SELECT name, visitDate, comment FROM comments LIMIT 4")
#     return render_template('newComment.html', comments=all_comments)
# @app.route("/guest_book/")
# def guest_book():
#     all_comments = query_db("SELECT name, visitDate, comment FROM comments LIMIT 4")
#     return render_template('newComment.html', comments=all_comments)
@app.route("/")
def hello_world():
    last_comments = query_db("SELECT name, visitDate, comment FROM comments LIMIT 4")
    return render_template('newComment.html', comments=last_comments)


#
#
# @app.route('/hello/')
# @app.route('/hello/<name>')
# def hello(name=None):
#     return render_template('hello.html', name=name)

@app.route('/comment/', methods=["POST"])
def comment():
    query_db("""
        CREATE TABLE IF NOT EXISTS comments(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
            name VARCHAR(100),
            visitDate DATE,
            comment VARCHAR(500)
        )
    """)
    query_db("INSERT INTO comments VALUES(NULL,?,?,?)",
             request.form['name'],
             request.form['visitDate'],
             request.form['comment'],
             )
    # con.commit()
    return str('données enregistrées')


@app.route('/comments/')
def comments():
    all_comments = query_db("SELECT name, visitDate, comment FROM comments")
    # for comment in comments:
    #    return str((comment['name'], comment['visitDate'], comment['comment']))
    return render_template('view_comments.html', comments=all_comments)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(debug=True, host='0.0.0.0')
    app.run(debug=True, host='127.0.0.1')

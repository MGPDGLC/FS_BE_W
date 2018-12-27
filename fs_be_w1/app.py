# coding: utf8
from model import User
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import os
import sys
import click
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired
from functools import wraps
app = Flask(__name__)

app.config["DATABASE"] = 'database.db'
app.config["SECRET_KEY"] = 'dark soul three'


def connect_db():
    """Connects to the specific database."""
    db = sqlite3.connect(app.config['DATABASE'])
    return db


def init_db():
    with app.app_context():
        db = connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


def insert_user_to_db(user):
    user_attrs = user.getAttrs()
    values = "VALUES("
    last_attr = user_attrs[-1]
    for attr in user_attrs:
        if attr != last_attr:
            values += "?,"
        else:
            values += "?"
    values += ")"
    sql_insert = "INSERT INTO users" + str(user_attrs) + values
    args = user.toList()
    g.db.execute(sql_insert, args)
    g.db.commit()


def query_users_from_db():
    users = []
    sql_select = "SELECT * FROM users"
    args = []
    cur = g.db.execute(sql_select, args)
    for item in cur.fetchall():
        user = User()
        user.fromList(item[1:])
        users.append(user)
    return users


def query_user_by_email(user_email):
    sql_select = "SELECT * FROM users where email=?"
    args = [user_email]
    cur = g.db.execute(sql_select, args)
    items = cur.fetchall()
    if len(items) < 1:
        return None
    first_item = items[0]
    user = User()
    user.fromList(first_item[1:])
    return user


def delete_user_by_email(user_email):
    delete_sql = "DELETE FROM users WHERE email=?"
    args = [user_email]
    g.db.execute(delete_sql, args)
    g.db.commit


def update_user_by_email(old_email, user):
    update_str = ""
    user_attrs = user.getAttrs()
    last_attr = user_attrs[-1]
    for attr in user_attrs:
        if attr != last_attr:
            update_str += attr + "=?,"
        else:
            update_str += attr + "=?"
    sql_update = "UPDATE users SET" + update_str + "WHERE email=?"
    args = user.tolist()
    args.append(old_email)
    g.db.execute(sql_update, args)
    g.dbcommit()


# 登录监视器检查登录状态
def user_login_reg(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if"user_email"not in session:
            return redirect(url_for("user_login",next=request.url))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/')
@user_login_reg
def index():
    print(session)
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def user_login():
    if request.method == "POST":
        useremail = request.form["user_email"]
        userpwd = request.form["user_pwd"]
        # 查看用户是否存在
        user_x = query_user_by_email(useremail)
        if not user_x:
            flash("用户不存在!", category='error')
            return render_template('user_login.html')
        else:
            if str(userpwd) != str(user_x.pwd):
                flash("密码错误!", category='error')
                return render_template('user_login.html')
            else:
                session["user_email"] = user_x.email
                return render_template('index.html')
    return render_template('user_login.html')


@app.route('/logout/')
@user_login_reg
def logout():
    # remove the username from the session if it's there
    session.pop('user_email', None)
    session["logged_in"] = False
    flash('您已退出登录', category='right')
    return redirect(url_for('index'))


@app.route('/regist/', methods=['GET', 'POST'])
def user_regist():
    if request.method == "POST":
        print(request.form)
        user = User()
        user.name = request.form["user_name"]
        user.pwd = request.form["user_pwd"]
        user.email = request.form["user_email"]
        user.age = request.form["user_age"]
        user.birthday = request.form["user_birthday"]
        user.face = request.form["user_face"]
        # 如果用户不存在，执行插入操作
        insert_user_to_db(user)
        flash("注册成功!", category='okey')
        return redirect(url_for("user_login", useremail=user.email))
    return render_template('user_regist.html')


# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret string')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# handlers
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Note=Note)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# Forms
class NewNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditNoteForm(FlaskForm):
    body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Update')


class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')


# Models
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    # optional
    def __repr__(self):
        return '<Note %r>' % self.body


@app.route('/bbs')
@user_login_reg
def bbs():
    form = DeleteNoteForm()
    notes = Note.query.all()
    return render_template('bbs.html', notes=notes, form=form)


@app.route('/new', methods=['GET', 'POST'])
@user_login_reg
def new_note():
    form = NewNoteForm()
    if form.validate_on_submit():
        body = form.body.data
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('留言成功！')
        return redirect(url_for('bbs'))
    return render_template('new_note.html', form=form)


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@user_login_reg
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('留言已更新')
        return redirect(url_for('bbs'))
    form.body.data = note.body  # preset form input's value
    return render_template('edit_note.html', form=form)


@app.route('/delete/<int:note_id>', methods=['POST'])
@user_login_reg
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        flash('留言已删除')
    else:
        abort(400)
    return redirect(url_for('bbs'))


if __name__ == '__main__':
    app.run()


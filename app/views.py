

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from app import app

from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_login(form.login.data)
        if user is None or not user.check_password(form.password.data):
            flash('invalid login or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(login=form.login.data,
                    FIO=form.FIO.data,
                    room_number=int(form.room_number.data),
                    organizer=form.is_organizer.data)
        user.set_password(form.password.data)
        photo = form.photo.data
        if photo is not None and photo.filename != '':
            pass

    return render_template('register.html', title='Register', form=form)




import os

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app

from app.forms import LoginForm, RegistrationForm, EditProfileForm, CommentForm, EventForm
from app.models import User, Event_type, User_event_type, Event, Place, Comment, User_on_event


@app.route('/')
@login_required
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
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(id=0,
                    login=form.login.data,
                    FIO=form.FIO.data,
                    room_number=int(form.room_number.data),
                    organizer=form.is_organizer.data,
                    photo=None,
                    password_hash=None)
        user.set_password(form.password.data)
        photo = form.photo.data
        if photo is not None and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.photo = 'photos/' + filename
        if not User.add(user):
            abort(500)
        flash('you registered')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<login>')
@login_required
def user(login):
    user = User.get_by_login(login)
    if user is None:
        abort(404)
    types = User_event_type.get_user_types(user.id)
    return render_template('user.html', title=user.login, user=user, types=types)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    choices = Event_type.get_all_types()
    if choices is None:
        choices = []
    form.types.choices = choices
    if form.validate_on_submit():
        FIO = form.FIO.data
        room_numbeer = form.room_number.data
        photo = form.photo.data
        if photo is not None and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo = 'photos/' + filename
            success = User.update(current_user.id, FIO, room_numbeer, photo)
        else:
            success = User.update(current_user.id, FIO, room_numbeer)
        if not success:
            abort(500)
        # после обновления пользователя обновляем его избранные типы ммероприятий
        if len(form.types.data) > 0:
            if not User_event_type.delete_by_user_id(current_user.id):
                abort(500)
            for ev_type_id in form.types.data:
                if not User_event_type.add(current_user.id, ev_type_id):
                    abort(500)
        return redirect(url_for('user', login=current_user.login))
    elif request.method == 'GET':
        # если только отрисовываем страницу то внесём старые значения в форму
        form.FIO.data = current_user.FIO
        form.room_number.data = current_user.room_number
    return render_template('edit_profile.html', title='Edit profile', form=form)


@app.route('/events')
@login_required
def events():
    event_lst = Event.get_all_events()
    if event_lst is None:
        event_lst = []
    return render_template('events.html', title='Events list', events=event_lst)


@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.organizer:
        return redirect(url_for('index'))
    form = EventForm()
    types = Event_type.get_all_types()
    if types is None:
        types = []
    form.types.choices = types
    places = Place.get_all_places()
    if places is None:
        places = []
    else:
        places = [(place.id, place.name) for place in places]
    form.places.choices = places
    if form.validate_on_submit():
        event = Event(0, form.name.data,
                      form.description.data, None,
                      form.types.data, form.places.data,
                      current_user.id)
        photo = form.photo.data
        if photo is not None and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo = 'photos/' + filename
            event.photo = photo
        else:
            flash('not valid file or filename')
            return redirect(url_for('add_event'))
        if not Event.add(event):
            abort(500)
        return redirect(url_for('events'))
    return render_template('add_event.html', title='add event', form=form)


@app.route('/register_on_event/<event_id>')
@login_required
def register_on_event(event_id):
    if not User_on_event.add(current_user.id, event_id):
        abort(500)
    return redirect(url_for('event', event_id=event_id))


@app.route('/unregister_on_event/<event_id>')
@login_required
def unregister_on_event(event_id):
    if not User_on_event.delete(current_user.id, event_id):
        abort(500)
    return redirect(url_for('event', event_id=event_id))


@app.route('/event/<event_id>', methods=['GET', 'POST'])
@login_required
def event(event_id):
    ev = Event.get_by_id(event_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(0,
                          form.message.data,
                          form.grade.data,
                          ev.id,
                          current_user.id)
        if not Comment.add(comment):
            abort(500)
        return redirect(url_for('event', event_id=ev.id))
    place = Place.get_by_id(ev.place_id)
    event_type = Event_type.get_by_id(ev.event_type_id)
    organizer = User.get_by_id(ev.organiser_id)
    comments = Comment.get_by_event_id(ev.id)
    is_there = User_on_event.is_there(current_user.id, ev.id)
    return render_template('event.html', title=f"event {ev.name}", event=ev, form=form, comments=comments, place=place, event_type=event_type, organizer=organizer, is_there=is_there)


@app.route('/users_on_event/<event_id>')
@login_required
def users_on_event(event_id):
    ev = Event.get_by_id(event_id)
    users = User_on_event.get_users_by_event_id(event_id)
    if users is None:
        users = []
    return render_template('users_on_event.html', title='users on event', users=users, event=ev)

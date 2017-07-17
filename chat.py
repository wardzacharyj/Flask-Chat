from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import func


from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import json

import time





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)

app.secret_key = "this is a terrible secret key"


###########################################################################################
#                           Model For Application                                         #
###########################################################################################


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r %r>' % (self.id, self.username)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "password": self.password,
        }


class Chatroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.String(30), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    def __init__(self, owner_id, name):
        self.owner_id = owner_id
        self.name = name

    def __repr__(self):
        return '<ChatRoom %r %r>' % (self.owner_id, self.name)

    def as_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_name = db.Column(db.Integer, db.ForeignKey('user.name'), nullable=False)
    message = db.Column(db.String(140), nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __init__(self, room_id, sender_id, sender_name, message, time):
        self.room_id = room_id
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.message = message
        self.time = time

    def __repr__(self):
        return '<Message = %r %r %r %r %r %r >' % (self.id, self.room_id, self.sender_id,
                                                   self.sender_name, self.message, self.time)

    def as_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "message": self.message,
            "time": self.time
        }


@app.cli.command('initdb')
def initdb_command():
    db.drop_all()
    db.create_all()

    print('Initialized database.')


###########################################################################################
#                                    Controller                                           #
###########################################################################################


def build_user(u):
    my_rooms = [r.as_dict() for r in Chatroom.query.filter_by(owner_id=u['id']).all()]
    for x in my_rooms:
        del x['owner_id']

    all_rooms = [all_r.as_dict() for all_r in Chatroom.query.filter(Chatroom.owner_id != u['id']).all()]
    for r in all_rooms:
        owner_name = User.query.filter_by(id=r['owner_id']).first().name
        r['owner_name'] = owner_name
        del r['owner_id']

    return {
        'id': u['id'],
        'name': u['name'],
        'my_room': my_rooms,
        'all_rooms': all_rooms
    }


def verify_user(u, p):
    valid_user = User.query.filter(and_(User.username == u, User.password == p)).first()
    if valid_user:
        session['user'] = valid_user.as_dict()
        session['user']['active_room'] = -1
        session.modified = True


def verify_room_owner(user_id, room_id):
    valid_owner = Chatroom.query.filter(and_(Chatroom.owner_id == user_id, Chatroom.id == room_id,)).first()
    if valid_owner:
        return True
    else:
        return False


def delete_chatroom(room_id):
    valid_owner = Chatroom.query.filter_by(id=room_id).first()
    db.session.delete(valid_owner)
    db.session.commit()


def room_exists(room_id):
    r = Chatroom.query.filter_by(id=room_id).first()
    if r:
        return True
    else:
        return False


def recent_users(room_id):
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    raw_user_info = Message.query.distinct(Message.sender_id).filter(
        and_(Message.room_id == room_id, Message.time >= five_min_ago, Message.sender_id != session['user']['id']))
    active_users = []
    for user in raw_user_info:
        active_users.append(user.sender_name)

    return active_users


def get_all_rooms(current_user_id):

    my_rooms = [m.as_dict() for m in Chatroom.query.filter_by(owner_id=current_user_id).all()]
    for ro in my_rooms:
        del ro['owner_id']

    other_rooms = [r.as_dict() for r in Chatroom.query.filter(Chatroom.owner_id != current_user_id).all()]
    for ro in other_rooms:
        owner_name = User.query.filter_by(id=ro['owner_id']).first().name
        ro['owner_name'] = owner_name
        del ro['owner_id']

    return {
        'my_rooms': my_rooms,
        'other_rooms': other_rooms
    }


def get_room_info(active_user, room_id):
    selected_room = (Chatroom.query.filter_by(id=room_id).first()).as_dict()
    return {
        'id': selected_room['id'],
        'owner_id': selected_room['owner_id'],
        'room_name': selected_room['name'],
        'sender_name': active_user['name'],
        'sender_id': active_user['id'],
        'users': recent_users(room_id)
    }


def add_user(name, username, password):
    if User.query.filter_by(username=username).first():
        return False
    else:
        user = User(name, username, password)
        db.session.add(user)
        db.session.commit()
        return True


def add_room(user_id, room_name):
    if Chatroom.query.filter_by(name=room_name).first():
        return True
    else:
        new_room = Chatroom(user_id, room_name)
        db.session.add(new_room)
        db.session.commit()
        return True


def send_message_to(room_id, message, user):
    try:
        message = Message(room_id, user['id'], user['name'], message, datetime.utcnow())
        db.session.add(message)
        db.session.commit()
        return True
    except IntegrityError:
        flash('Message Failed to Send')
        return False


def get_messages_since(chat_room_id, most_recent_id):
    if db.session.query(Message.id).count() == 0:
        return {
            'recent_messages': {},
            'most_recent_id': -1
        }

    if most_recent_id == -1:
        most_recent_id = db.session.query(func.max(Message.id)).first()
        most_recent_id = most_recent_id[0]

    print(most_recent_id)
    raw_messages = Message.query.filter(Message.room_id == chat_room_id, Message.id > most_recent_id).all()

    recent_messages = [m.as_dict() for m in raw_messages]
    new_offset = len(recent_messages)

    for x in recent_messages:
        if x['sender_id'] == session['user']['id']:
            x['type'] = 'outbound'
        else:
            x['type'] = 'inbound'
        x['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        del x['room_id']

    return {
        'recent_messages': recent_messages,
        'most_recent_id': most_recent_id+new_offset
    }


###########################################################################################
#                                    Routes                                               #
###########################################################################################


@app.route("/")
def splash():
    if 'user' in session:
        return redirect(url_for('home'))
    else:
        return render_template("splash.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("splash"))
    else:
        usr = request.form['username']
        pw = request.form['password']

        if len(usr) == 0 and len(pw) == 0:
            flash("Please fill out all the fields")
        else:
            verify_user(usr, pw)
            if 'user' in session:
                return redirect(url_for('home'))
            else:
                flash('That User Does not exist in the database')
                return redirect(url_for('splash'))


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return redirect(url_for("splash"))
    else:
        name = request.form['name']
        usr = request.form['username']
        pw = request.form['password']
        if add_user(name, usr, pw):
            verify_user(usr, pw)
            return redirect(url_for("home"))
        else:
            flash('Sorry a user with that username already exists')
            return redirect(url_for("splash"))


@app.route("/home")
def home():
    if 'user' in session:
        session['home'] = build_user(session['user'])
        return render_template("home.html", user=session['home'])
    else:
        return redirect(url_for("splash"))


@app.route('/room/<int:room_id>')
def room(room_id):
    if 'user' in session and room_exists(room_id):
        session['user']['active_room'] = room_id
        session.modified = True
        return render_template("home.html", room=get_room_info(session['user'], room_id))
    else:
        return redirect(url_for("home"))


@app.route('/exit_room/<int:room_id>', methods=['POST'])
def exit_room(room_id):
    if 'user' in session and room_exists(room_id):
        session['user']['active_room'] = -1
        session.modified = True
        return '/home'
    else:
        return 'Failed'


@app.route('/create_room', methods=["POST"])
def create_room():
    if request.json['name'] and 'user' in session:
        add_room(session['user']['id'], request.json['name'])
        return 'Success'
    else:
        return 'Failed'


@app.route('/delete_room/<int:room_id>', methods=["POST"])
def delete_room(room_id):
    if 'user' in session:
        is_valid = verify_room_owner(session['user']['id'], room_id)
        print('Here', is_valid)
        if is_valid:
            delete_chatroom(room_id)
            print('here')
            return 'Success'
    # Do not provide info about room client doesn't need
    return 'That room does not exist'


@app.route('/poll_rooms', methods=["GET"])
def poll_room():
    if 'user' in session:
        rooms_json = json.dumps(get_all_rooms(session['user']['id']))
        return rooms_json
    else:
        return 'Failed'


@app.route('/send/<int:room_id>', methods=["POST"])
def send_message(room_id):
    if 'user' in session:
        if 'message' in request.json:
            was_sent = send_message_to(room_id, request.json['message'], session['user'])
            if was_sent:
                return 'Success'

    return 'Failed'


@app.route('/get_messages/<int:room_id>', methods=["POST"])
def get_messages(room_id):

    if 'user' in session and 'most_recent_room_id' in request.json:
        print(session['user'])
        if session['user']['active_room'] == -1:
            return json.dumps({
                'redirect': '/home'
            })
        if room_id != session['user']['active_room']:
            return json.dumps({
                'redirect': '/room/'+str(session['user']['active_room'])
            })
        elif room_exists(room_id):
            a = get_messages_since(room_id, request.json['most_recent_room_id'])
            print(a)
            return json.dumps(a)
        else:
            return json.dumps({
                'error': 'ROOM DELETED'
            })

    return redirect(url_for('home'))


@app.route('/logout',  methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("splash"))


if __name__ == '__main__':
    app.run()

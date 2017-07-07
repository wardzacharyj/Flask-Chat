from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catering.db'
db = SQLAlchemy(app)

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


class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.String(30), db.ForeignKey('user.id'), nullable=False, unique=True)
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
#                                    Routes                                               #
###########################################################################################

app.secret_key = "this is a terrible secret key"


@app.route("/")
def splash():
    return render_template("splash.html")


@app.route("/home")
def home():

    user = {
        'id': 1,
        'name': 'name',
        'my_room': [
            {
                'id': 2,
                'room_name': 'The Best Room'
            },
            {
                'id': 3,
                'room_name': 'The Best Room 2'
            }

        ],
        'all_rooms': [
            {
                'id': 4,
                'room_name': 'Main Room 1',
                'room_owner': 'owner of main room 1'
            },
            {
                'id': 5,
                'room_name': 'Main Room 2',
                'room_owner': 'owner of main room 2'
            },

        ]
    }

    return render_template("dashboard.html", user=user)


@app.route('/room/<int:room_id>')
def room(room_id):

    r = {
        'id': 2,
        'owner_id': 1,
        'room_name': 'The Best Room',
        'sender_name': 'Zach',
        'sender_id': 1,
        'users': ['Zach', 'Ian', 'Molly']
    }

    return render_template("dashboard.html", room=r)


if __name__ == '__main__':
    app.run()

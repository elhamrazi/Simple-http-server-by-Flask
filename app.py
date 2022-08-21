from flask import Flask
from flask import request
from flask import Response
from flask_login import LoginManager, login_required
from flask_login import login_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user


from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'secret-key'
login_manager.login_view = '/admin/login'


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.filter_by(id=user_id).first()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80), nullable=False)
    light = db.Column(db.Float)
    office = db.Column(db.Integer, db.ForeignKey('office.id'), nullable=False)
    room = db.Column(db.Integer, nullable=False)


class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lightsOn = db.Column(db.Integer, nullable=False)
    lightsOff = db.Column(db.Integer, nullable=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    office = db.Column(db.Integer, db.ForeignKey('office.id'), nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    office = db.Column(db.Integer, db.ForeignKey('office.id'), nullable=False)
    datetime = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Text)


@app.route('/office/register', methods=['POST'])
def register():
    request_json = request.get_json()
    lightsOn = int(request_json["lightsOnTime"])
    lightsOff = int(request_json["lightsOffTime"])
    office = Office(lightsOn=lightsOn, lightsOff=lightsOff)
    db.session.add(office)
    db.session.commit()
    return Response({'office added'})


@app.route('/admin/<name1>', methods=['POST'])
def admin_handle(name1):
    if name1 == 'login':
        request_json = request.get_json()
        username = str(request_json["username"])
        password = str(request_json["password"])

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            login_user(admin)
            return Response("welcome Admin!")
        else:
            return Response("admin not found", status=401)
    elif name1 == 'register':
        request_json = request.get_json()
        office_id = str(request_json["office"])
        username = str(request_json["username"])
        password = str(request_json["password"])

        # office = Office.query.filter_by(id=office_id).first()
        admin = Admin(username=username, password=password, office=office_id)
        db.session.add(admin)
        db.session.commit()
        return Response({'admin added'})


@app.route('/admin/user/register', methods=['POST'])
def register_user():
    if current_user.is_authenticated:
        request_json = request.get_json()
        password = str(request_json["password"])
        office = int(request_json["office"])
        light = int(request_json["light"])
        room = int(request_json["room"])
        user = User(password=password, office=office, light=light, room=room)
        db.session.add(user)
        db.session.commit()
        return Response({'user added'})
    else:
        return Response('you need to login as an admin first')


@app.route('/admin/activities', methods=['GET'])
def see_activities():
    if current_user.is_authenticated:
        activities = Activity.query.all()
        res = ""
        for a in activities:
            res += "user: " + str(a.user) + " time: " + str(a.datetime) + " type: " + str(a.type) + " office: " + str(a.office)
        return Response(res)
    else:
        return Response('you need to login as an admin first')


@app.route('/admin/setlights', methods=['POST'])
def set_lights():
    if current_user.is_authenticated:
        request_json = request.get_json()
        light_on = int(request_json["lightOn"])
        light_out = int(request_json["lightOff"])
        office_id = int(request_json["office"])
        office = Office.query.filter_by(id=office_id).first()
        office.lightsOn = light_on
        office.lightsOff = light_out
        db.session.commit()
        return Response('office light hours set')

    else:
        return Response('you need to login as an admin first')


if __name__ == '__main__':
    app.run()

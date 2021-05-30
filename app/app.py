from flask import Flask, render_template, flash, request,g, url_for, session, jsonify, redirect
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os
from form import LoginForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret'
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

class User:
    def __init__(self,id,username,password):
        self._id = id
        self._username = username
        self._password = password
        self._email = None
    def __init__(self,id,username,password,email):
        self._id = id
        self._username = username
        self._password = password
        self._email = email

    def __repr__(self):
        return f'Hello User: {self._username}'


userList = []
userList.append(User('trminhhien17','trminhhien17','minhhien1772000@gmail.com'))
userList.append(User('notm16','notm16','minhtri2000@gmail.com'))
userList.append(User('dinhhuy','dinhhuy'))





db = SQLAlchemy(app)
user = {"username":"trminhhien17"}


# class Todo(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     content = db.Column(db.String(200),nullable =False)
#     completed = db.Column(db.Integer,default = 0)
#     date_created = db.Column(db.DateTime, default = datetime.utcnow)
#
#     def __repr__(self):
#         return '<Task %r' %self.id
#
# class User(db.Model):
#
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#
#     def __repr__(self):
#         return '<User %r>' % self.username



@app.route('/register')
def register():
    return render_template('signup.html')


@app.route('register',method = 'POST')
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    user = User.q

@app.route("/")
def displayHomePage():
    return redirect('/index')

@app.route("/index")
def displayIndexPage():
    # return render_template('index.html', title = "Home", user = user)
    return render_template("index.html",title = "Home page", user =user)

# @app.route("/login", methods = ['GET','POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data));
#         return redirect('/index')

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in userList if x._id == session['user_id']][0]
        g.user = user

@app.route('/login',methods = ['GET','POST'])
def login():

    if request.method == 'POST':
        session.pop('user_id',None)

        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user = [x for x in userList if x._username == username][0]
        if user and user._password == password:
            session['user_id'] = user._id
            return redirect(url_for('profile'))
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))



if __name__ == "__main__":
    app.run(debug=True)
    ##
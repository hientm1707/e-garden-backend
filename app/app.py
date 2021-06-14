from flask import Flask, render_template, flash, request,g, url_for, session
from flask.json import jsonify
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
# from form import LoginForm
from werkzeug.utils import redirect
from process_data import publish_data, receive_new_data, get_mqtt, global_data
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
socketio = SocketIO(app)
class User:
    def __init__(self,id,username,password = None , email = None):
        self._id = id
        self._username = username
        self._password = password
        self._email = email
    # def __init__(self,id,username,password,email):
    #     self._id = id
    #     self._username = username
    #     self._password = password
    #     self._email = email

    def __repr__(self):
        return f'Hello User: {self._username}'


userList = []
userList.append(User('trminhhien17','trminhhien17','minhhien1772000@gmail.com'))
userList.append(User('notm16','notm16','minhtri2000@gmail.com'))
userList.append(User('dinhhuy','dinhhuy'))





db = SQLAlchemy(app)
user = {"username":"huydinh"}


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

@app.route("/api/account/<username>/<topic_id>", methods=["POST"])
def send_data(username, topic_id):
    data = request.get_json()
    value = data['value']
    # param = request.args.get("param")
    if value:
        return publish_data(username, topic_id, value)
    return f"Couldn't work with param = {value}"

@app.route("/api/account/data", methods=["GET"])
def get_new_data():
    return receive_new_data()


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

@socketio.on('connection')
def handle_connection(json):
    socketio.emit('connection', 'true')
    print('client connected')

@socketio.on('client-listen-data')
def handle_client_need_data(data):
    print(jsonify(data))
    socketio.emit('server-send-mqtt', get_mqtt() )



if __name__ == "__main__":
    app.run(debug=True)
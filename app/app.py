from flask import Flask, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from form import LoginForm
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

user = {"username":"trminhhien17"}


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200),nullable =False)
    completed = db.Column(db.Integer,default = 0)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Task %r' %self.id

@app.route("/")
def displayHomePage:
    return redirect('/index')


@app.route("/login", methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data));
        return redirect('/index');


@app.route("/index")
def displayIndexPage():
    # return render_template('index.html', title = "Home", user = user)
    return render_template("index.html",title = "Home page", user =user)


if __name__ == "__main__":
    app.run(debug=True)
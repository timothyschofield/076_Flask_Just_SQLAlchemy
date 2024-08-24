"""

    This does NOT use the Flask-SQLAlchemy extension
    Just Flask and SQLAchemy separately 
    SQLAchemy uses the declarative pattern

    24 August 2024
    
    To run:
    In terminal
    export FLASK_APP=app
    export FLASK_ENV=development
    flask run
    
    Ctrl-C to quit
    
    Go to http://127.0.0.1:5000

"""
import os

from flask import Flask, render_template, request, url_for, redirect

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = 'sqlite:///' + os.path.join(basedir, 'project.db')

engine = create_engine(db_path, echo=True)
session = Session(engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, email={self.email!r})" 


#########################################
Base.metadata.create_all(engine)
#########################################
# print(f"Tables are:{Base.metadata.tables}")

# Landing page - no action 
@app.route('/')
def index():
    return render_template('index.html')


# Display all users
@app.route("/users")
def user_list():
    stmt = select(User).order_by(User.username)
    users = session.execute(stmt).scalars()       # what does scalars() mean?

    return render_template("user/list.html", users=users)


# Create new user
@app.route("/user/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":

        user = User(username=request.form["username"], email=request.form["email"])
        
        session.add(user)
        session.commit()
        return redirect(url_for("user_detail", id=user.id))

    return render_template("user/create.html")


# Display the details of a single user
@app.route("/user/detail/<int:id>")
def user_detail(id):
    
    user = session.get(User, id)
    if user == None:
        message = f"User id: {id} not found"
        return render_template("404.html", message=message)
    else:
        return render_template("user/detail.html", user=user)


# Edit a single user
@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def user_edit(id):
    
    user = session.get(User, id)
    if user == None:
        message = f"User id: {id} not found"
        return render_template("404.html", message=message)
    else:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']

            user.username = username
            user.email = email

            session.add(user)
            session.commit()

            return redirect(url_for("user_detail", id=user.id))

    return render_template('user/edit.html', user=user)


# Delete a single user
@app.route("/user/delete/<int:id>", methods=["GET", "POST"])
def user_delete(id):
    user = session.get(User, id)
    if user == None:
        message = f"User id: {id} not found"
        return render_template("404.html", message=message)
    else:
        if request.method == "POST":
            session.delete(user)
            session.commit()
            return redirect(url_for("user_list"))

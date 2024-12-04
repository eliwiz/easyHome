#google mapes (guest will ask for address, user already has it logged in to check for distance)
#new page on professional names with more details (name, address, past work, map)
#book button (user info, requests picture and description, date and time for appointment)
#fix feedback
#hook up to database
#set up character limits and update registration
#email verification

#imports
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os, io
from werkzeug.utils import secure_filename
from sqlalchemy import desc, asc
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from flask_mail import Message
from flask_login import LoginManager, UserMixin
from flask_login import login_user, current_user, logout_user, login_required


app = Flask(__name__)

#routes
@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route('/professionals', methods=["GET", "POST"])
def professionals():
    if request.method == "POST":
        search = request.form.get("search")
        flash(f"Searched up {search}", "success")
        
    return render_template("professionals.html")
    
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # email = request.form.get("email")
        # password = request.form.get("password")
        # password2 = request.form.get("password2")
        # flash(f"Logged in with email {email} and password {password} with confirmation password of {password2}", "success")
        pass
    return render_template("register.html")

@app.route("/registerCustomer", methods=["GET", "POST"])
def registerCust():
    return render_template("registerCust.html")

@app.route("/registerProfessional", methods=["GET", "POST"])
def registerProf():
    return render_template("registerProf.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email)
        print(password)
        print("AJ")
        flash(f"Logged in with email {email} and password {password}", "success")
    return render_template("login.html")


@app.route('/professional/<id>', methods=["GET", "POST"])
def professionalPage(id):
    return render_template("profPage.html", id=id)

@app.route('/full', methods=["GET", "POST"])
def indexfull():
    return render_template("index_full.html")

@app.route('/test')
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.secret_key = "jfvdjhklvdfhgspierytuepsri5uw43hkjlh" 
    app.run(debug=True, port="9000")
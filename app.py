#google mapes (guest will ask for address, user already has it logged in to check for distance)
#new page on professional names with more details (name, address, past work, map)
#book button (user info, requests picture and description, date and time for appointment)
#fix feedback
#hook up to database
#set up character limits and update registration
#email verification

#imports
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from markupsafe import Markup, escape
import os, io
from werkzeug.utils import secure_filename
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from flask_mail import Message
from flask_login import LoginManager, UserMixin
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc, LargeBinary



from database import init_db
con = sqlite3.connect("database.db")


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
    return render_template("register.html")

@app.route("/registerCustomer", methods=["GET", "POST"])
def registerCust():
    fname = request.form.get("fname")
    mname = request.form.get("mname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    user = request.form.get("user")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    phone = request.form.get("phone")
    gender = request.form.get("gender")
    apt = request.form.get("street/atp")
    street = request.form.get("street")
    town = request.form.get("town")
    state = request.form.get("state")
    zip = request.form.get("zip")
    
    if password != password2:
        flash("Please make sure that your passwords match!", "warning")
    if add_cust(fname, mname, lname, gender, phone, email, password):
        flash("User registered successfully!", "success")
        return redirect(url_for("index"))
    else:
        flash("An error occurred while registering the user.", "danger")
    
    return render_template("registerCust.html")

@app.route("/registerProfessional", methods=["GET", "POST"])
def registerProf():
    return render_template("registerProf.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        print(email)
        password = request.form.get("password")
        print(password)
        user = get_user_by_email(email)  
        print(user) 
        print(user[7])    
        if user and user[7] == password:
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials!","danger")
    return render_template("login.html")

@app.route('/professional/<id>', methods=["GET", "POST"])
def professionalPage(id):
    if request.method == "POST":
        zipcode = request.form.get("zipcode")
        if zipcode:
            # Replace with your actual Google Maps Embed API key
            api_key = "AIzaSyDmYpBjV12iq8-83OxZMK8aujT1AWxb8Sc"
            iframe_html = Markup(f"""
            <iframe
              width="600"
              height="450"
              style="border:0"
              loading="lazy"
              allowfullscreen
              referrerpolicy="no-referrer-when-downgrade"
              src="https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={zipcode}&destination=City+Hall,New+York,NY">
            </iframe>
            """)
            return jsonify({"iframe": str(iframe_html)})
        else:
            return jsonify({"error": "No ZIP code provided."}), 400  # Bad request
    return render_template("profPage.html", id=id)

@app.route('/full', methods=["GET", "POST"])
def indexfull():
    return render_template("index_full.html")

@app.route('/test')
def test():
    return render_template("test.html")

#FUNCTIONS

def get_all_users():
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users")
        users = c.fetchall()

        return users  
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []
    finally:
        if conn:
            conn.close()
            
def get_user_by_email(email):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()  

        return user
    except sqlite3.Error as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_cust(first_name, middle_name, last_name, gender, phone_number, email, password):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO users (first_name, middle_name, last_name, gender, phone_number, email, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, middle_name, last_name, gender, phone_number, email, password))

        conn.commit()
        print("User added successfully")
        return True  
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
        return False 
    finally:
        if conn:
            conn.close()


def add_prof(first_name, middle_name, last_name, gender, phone_number, email, password):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO users (first_name, middle_name, last_name, gender, phone_number, email, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, middle_name, last_name, gender, phone_number, email, password))

        conn.commit()
        print("User added successfully")
        return True  
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
        return False 
    finally:
        if conn:
            conn.close()



if __name__ == "__main__":
    app.secret_key = "jfvdjhklvdfhgspierytuepsri5uw43hkjlh" 
    init_db()
    app.run(debug=True, port="9000")
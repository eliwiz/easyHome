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
con.row_factory = sqlite3.Row

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #specify the login route
# Set custom messages
login_manager.login_message = "Unauthorized Access! Please log in!"
login_manager.login_message_category = "danger"

class User(UserMixin):
    def __init__(self, user_row):
        if user_row:  
            self.id = user_row["id"]
            self.first_name = user_row["first_name"]
            self.middle_name = user_row["middle_name"]
            self.last_name = user_row["last_name"]
            self.phone_number = user_row["phone_number"]
            self.email = user_row["email"]
            self.password = user_row["password"]  

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  # Enables row-based access
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = c.fetchone()

        # Return a User object if the user is found, otherwise return None
        return User(user_row) if user_row else None
    except sqlite3.Error as e:
        print(f"Error retrieving user by ID: {e}")
        return None
    finally:
        if conn:
            conn.close()

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
    if request.method == 'POST':
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
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        if c.fetchone() is not None:
            flash("Email already registered!","warning")
            return render_template("registerCust.html")
        
        c.execute("""
                  INSERT INTO users (
                  first_name, middle_name, last_name, gender, phone_number, email, password, street_number, street_name, town, state, zip_code)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,(fname,mname,lname,gender,phone,email,password,street_number,street_name,town,state,zip_code))
    
        conn.commit()
        flash("Registration successful! Please login.", "success")
        
        return redirect(url_for("login"))

    return render_template("registerCust.html")

@app.route("/registerProfessional", methods=["GET", "POST"])
def registerProf():
    if request.method == "POST":
        pass
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
           
        if user and user.password == password:
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
            
# def get_professionals():
#         try:
#             conn= sqlite3.connect("database.db")
            
#             c.execute("SELECT * FROM users WHERE ")
            
def get_user_by_email(email):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = c.fetchone()

        return User(user_row) if user_row else None  # Convert row to User object
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

def delete_user(user_id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

        if c.rowcount > 0:
            print(f"User with ID {user_id} deleted successfully")
            return True
        else:
            print(f"No user found with ID {user_id}")
            return False
    except sqlite3.Error as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        if conn:
            conn.close()

def edit_user(user_id, first_name, middle_name, last_name, gender, phone_number, email, password):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            UPDATE users 
            SET first_name = ?, middle_name = ?, last_name = ?, gender = ?, 
                phone_number = ?, email = ?, password = ?
            WHERE id = ?
        """, (first_name, middle_name, last_name, gender, phone_number, email, password, user_id))

        conn.commit()

        if c.rowcount > 0:
            print(f"User with ID {user_id} updated successfully")
            return True
        else:
            print(f"No user found with ID {user_id}")
            return False
    except sqlite3.Error as e:
        print(f"Error updating user: {e}")
        return False
    finally:
        if conn:
            conn.close()

@app.route('/logout')
@login_required
def logout():
    try: 
        logout_user()
        flash("You have been logged out!","success")
        return redirect(url_for('index'))
    except Exception as e:
        flash("An error occurred during logout.", "danger")
        return redirect(url_for('index'))



if __name__ == "__main__":
    app.secret_key = "jfvdjhklvdfhgspierytuepsri5uw43hkjlh" 
    init_db()
    app.run(debug=True, port="9000")
#google mapes (guest will ask for address, user already has it logged in to check for distance)
#new page on professional names with more details (name, address, past work, map)
#book button (user info, requests picture and description, date and time for appointment)
#hook up to database
#email verification
#functionality for searching (nearby zipcodes, within how many miles)


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
login_manager.login_view = 'login' 
# Login required messages
login_manager.login_message = "Unauthorized Access! Please log in!"
login_manager.login_message_category = "danger"

#SQL3 databases do not work with UserMixin, *should* create temporary object in order for UserMixin to work properly
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
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = c.fetchone()

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

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = get_user_by_email(email)  
           
        if user and user.password == password:
            login_user(user)
            flash(f"Welcome {user.first_name}", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials!","danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user() 
    flash("Logged out successfully", "success")
    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    list = get_all_users()
    if request.method == "POST":
        user_id = "delete_cart_item"
        delete_user(user_id)
    return render_template("admin.html", users=list)

#REGISTER PAGES
@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template("register.html")
   
@app.route("/registerCustomer", methods=["GET", "POST"])
def registerCust():
    if request.method == 'POST':
        if request.method == "POST":
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
        if add_cust(fname, mname, lname, gender, phone, email, password, apt, street, town, state, zip):
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

#Professional pages (viewing as customer)
@app.route('/professionals', methods=["GET", "POST"])
def professionals():
    list = get_all_users()
    if request.method == "POST":
        if "filters" in request.form:
            zip = request.form.get("zip_code")
            selected_distance = request.form.get("distance")
            
            if selected_distance != None:
                upper = int(zip) + int(selected_distance)
                lower = int(zip) - int(selected_distance)
                list = get_users_by_zip_range(int(lower), int(upper))
            else:
                list = get_users_by_zip(int(zip))
                
        
    return render_template("professionals.html", professionals=list)
 
@app.route('/professional/<id>', methods=["GET", "POST"])
def professionalPage(id):
    if request.method == "POST":
        zipcode = request.form.get("zipcode")
        if zipcode:
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

@app.route('/schedule/<id>', methods=["GET", "POST"])
@login_required
def bookprof():
    # if request.method == "GET":
    #     if request.args.get("profId"):
    #         profId = int(request.args.get("profId"))
    #         professional = get_user_by_id(profId)
    #         return render_template("bookProf.html", prof = professional)
    #     return redirect(url_for("index"))
    return render_template("bookProf.html")

#Customer onlt pages (checking things they booked, updating info)
@app.route("/editCustomer", methods=["POST", "GET"])
@login_required
def editCustomer():
    userInformation = get_user_by_id(current_user.id)
    return render_template("editCust.html", userInfo= userInformation)

@app.route("/manageBookings")
@login_required
def manageBookings():
    return render_template("manageBookings.html")

#Professional only pages (checking their appointments, updating info)
@app.route("/manageJobs", methods=['GET', "POST"])
@login_required
def manageJobs():
    return render_template("manageJobs.html")

@app.route("/editProfessional", methods=['GET', "POST"])
@login_required
def editProf():
    return render_template("editProf.html")

#Unimportant pages, likely to get cut at end
@app.route("/feedback", methods=["GET" , "POST"])
def feedback():
    return render_template("feedback.html")

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
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()
        
        c.execute("SELECT * FROM users")
        users = [dict(row) for row in c.fetchall()]  

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
            
def get_user_by_id(user_id):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = c.fetchone()

        return User(user_row) if user_row else None  
    except sqlite3.Error as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_by_email(email):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = c.fetchone()

        return User(user_row) if user_row else None  
    except sqlite3.Error as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_users_by_zip(zip_code):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()

        c.execute("""
            SELECT * FROM users
            WHERE zip_code = ?
        """, (zip_code,))

        user_row = c.fetchall()  
        return User(user_row) if user_row else None  

    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def get_users_by_zip_range(lower, upper):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()

        c.execute("""
            SELECT * FROM users
            WHERE zip_code BETWEEN ? AND ?
        """, (lower, upper))

        user_rows = c.fetchall()  
        return [User(row) for row in user_rows] 

    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []
    
    finally:
        if conn:
            conn.close()


def add_cust(first_name, middle_name, last_name, gender, phone_number, email, password, 
             street_number, street_name, town, state, zip_code):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO users (first_name, middle_name, last_name, gender, phone_number, email, password, 
                               street_number, street_name, town, state, zip_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, middle_name, last_name, gender, phone_number, email, password, 
              street_number, street_name, town, state, zip_code))

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
            

if __name__ == "__main__":
    app.secret_key = "jfvdjhklvdfhgspierytuepsri5uw43hkjlh" 
    init_db()
    app.run(debug=True, port="9000")
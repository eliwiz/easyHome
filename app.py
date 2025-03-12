#google mapes (guest will ask for address, user already has it logged in to check for distance)
#book button (user info, requests picture and description, date and time for appointment)
#email verification
#functionality for searching (nearby zipcodes, within how many miles)
#search by zip, show rows of email and phone number
#only show when booking an appointment^^
#send email to professional once appointment is made

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
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import desc, asc, LargeBinary

from database import init_db, reset_db
con = sqlite3.connect("database.db")
con.row_factory = sqlite3.Row

# reset_db()  # Resets the database
# init_db()   # Reinitializes the tables

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()

print("Existing tables:", tables)

conn.close()

app = Flask(__name__, static_folder="static")
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
    # check_columns()
    # add_review(customer_id=1, professional_id=2, rating=5, comment="Excellent work!")
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
    if request.method == "POST":
        fname = request.form.get("fname")
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
            return redirect(url_for("login"))
        if add_acc(fname, mname, lname, gender, phone, email, password, apt, street, town, state, zip, "customer"):
            flash("User registered successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("An error occurred while registering the user.", "danger")
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # c.execute("SELECT * FROM users WHERE email = ?", (email,))
        # if c.fetchone() is not None:
        #     flash("Email already registered!","warning")
        #     return render_template("registerCust.html")
        
        # c.execute("""
        #         INSERT INTO users (
        #         first_name, middle_name, last_name, gender, phone_number, email, password, street_number, street_name, town, state, zip_code)
        #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,(fname,mname,lname,gender,phone,email,password,street_number,street_name,town,state,zip_code))
    
        # conn.commit()
        # flash("Registration successful! Please login.", "success")
        
        return redirect(url_for("login"))
    return render_template("registerCust.html")

@app.route("/registerProfessional", methods=["GET", "POST"])
def registerProf():
    if request.method == "POST":
        fname = request.form.get("fname")
        mname = request.form.get("mname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        # user = request.form.get("user")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        phone = request.form.get("phone")
        gender = request.form.get("gender")
        apt = request.form.get("street/atp")
        street = request.form.get("street")
        town = request.form.get("town")
        state = request.form.get("state")
        special = request.form.get('service')
        zip = request.form.get("zip")
        hourly = int(request.form.get("hourly"))
        desc = request.form.get("desc")

        if password != password2:
            flash("Please make sure that your passwords match!", "warning")
            return redirect(url_for("login"))
            
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            # Register user first
            c.execute("""
                INSERT INTO users (first_name, middle_name, last_name, gender, phone_number, email, password, 
                                   street_number, street_name, town, state, zip_code, user_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (fname, mname, lname, gender, phone, email, password, apt, street, town, state, zip, "professional"))

            # Get user ID of newly registered professional
            user_id = c.lastrowid

            # Register as a professional
            if user_id:
                if add_prof(user_id, special, hourly, desc):
                    conn.commit()
                    flash("Professional registered successfully!", "success")
                    return redirect(url_for("index"))
                else:
                    flash("Error adding professional details.", "danger")

        except sqlite3.Error as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            conn.close()
        
        return redirect(url_for("login"))

    return render_template("registerProf.html")

#Professional pages (viewing as customer)
@app.route('/professionals', methods=["GET", "POST"])
def professionals():
    list = get_all_users()
    user_zip = ""
    if current_user.is_authenticated:
        user_zip = get_user_by_id(current_user.id).zip_code
        
    if request.method == "POST":
        if "filters" in request.form:
            zip = request.form.get("zip_code")
            selected_distance = request.form.get("distance")
            
            if selected_distance != None:
                upper = int(zip) + int(selected_distance)
                lower = int(zip) - int(selected_distance)
                list = get_users_by_zip_range(int(lower), int(upper))
                for user in list:
                    print(vars(user))  # Prints the attributes of each User object as a dictionary
            else:
                list = get_users_by_zip(int(zip))
        if "name" in request.form:
            name = request.form.get("search")
            list = get_users_by_name(name)
                
        
    return render_template("professionals.html", professionals=list, user_zip=user_zip)
 
# @app.route('/professional/<id>', methods=["GET", "POST"])
# def professionalPage(id):
#     if request.method == "POST":
#         zipcode = request.form.get("zipcode")
#         if zipcode:
#             api_key = "AIzaSyDmYpBjV12iq8-83OxZMK8aujT1AWxb8Sc"
#             iframe_html = Markup(f"""
#             <iframe
#               width="600"
#               height="450"
#               style="border:0"
#               loading="lazy"
#               allowfullscreen
#               referrerpolicy="no-referrer-when-downgrade"
#               src="https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={zipcode}&destination=City+Hall,New+York,NY">
#             </iframe>
#             """)
#             return jsonify({"iframe": str(iframe_html)})
#         else:
#             return jsonify({"error": "No ZIP code provided."}), 400  # Bad request
#     return render_template("profPage.html", id=id)

@app.route('/createReservation/<profId>', methods=["GET", "POST"])
@login_required
def createReservation(profId):
    if request.method == "GET":
        professional = get_user_by_id(profId)
        return render_template("createReservation.html", prof=professional)
    if request.method == "POST":
        prof_id = request.form.get("profID")
        title = request.form.get("title")
        description = request.form.get("desc")

        if add_work_detail(current_user.id, prof_id, title, description):
            flash("Professional created sucessfully!", "success")
            return url_for("manageReservations")
    return url_for("index")

#Customer onlt pages (checking things they booked, updating info)
@app.route("/editCustomer", methods=["POST", "GET"])
@login_required
def editCustomer():
    userInformation = get_user_by_id(current_user.id)
    return render_template("editCust.html", userInfo= userInformation)

@app.route("/manageReservations")
@login_required
def manageReservations():
    return render_template("manageReservations.html")

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
@app.route('/full', methods=["GET", "POST"])
def indexfull():
    return render_template("index_full.html")

@app.route('/test')
def test():
    return render_template("test.html")

#FUNCTIONS
def check_columns():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    for col in columns:
        print(col)
    conn.close()

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

            
def get_professionals():
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM professionals")
        professionals = [dict(row) for row in c.fetchall()]

        return professionals
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []
    finally:
        if conn:
            conn.close()

            
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

        c.execute("SELECT * FROM users WHERE zip_code = ?", (zip_code,))
        users = [dict(row) for row in c.fetchall()]

        print(users)  # Debugging line to check output
        return users  

    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

            
def get_users_by_name(name):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()

        c.execute("""
            SELECT * FROM users
            WHERE first_name LIKE ? OR last_name LIKE ?
        """, (f"%{name}%", f"%{name}%"))

        user_rows = c.fetchall()  
        return [User(row) for row in user_rows] 

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


def add_acc(first_name, middle_name, last_name, gender, phone_number, email, password, 
             street_number, street_name, town, state, zip_code, user_type):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO users (first_name, middle_name, last_name, gender, phone_number, email, password, 
                               street_number, street_name, town, state, zip_code, user_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, middle_name, last_name, gender, phone_number, email, password, 
              street_number, street_name, town, state, zip_code, user_type))

        conn.commit()
        print("User added successfully")
        return True  
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
        return False 
    finally:
        if conn:
            conn.close()

def add_work_detail(user_id, professional_id, work_id, work_name, work_description):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO workDetails (user_id, professional_id, work_name, work_description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, professional_id, work_name, work_description))

        conn.commit()
        print("Work detail added successfully")
        return True

    except sqlite3.Error as e:
        print(f"Error adding work detail: {e}")
        return False

    finally:
        conn.close()

def add_prof(user_id, profession, hourly_cost, description, is_verified=0):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO professionals (id, profession, hourly_cost, description, is_verified)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, profession, hourly_cost, description, is_verified))

        conn.commit()
        print("Professional added successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error adding professional: {e}")
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
            
            
def add_review(customer_id, professional_id, rating, comment):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO reviews (customer_id, professional_id, rating, comment)
            VALUES (?, ?, ?, ?)
        """, (customer_id, professional_id, rating, comment))

        conn.commit()
        print("Review added successfully")
        return True  
    except sqlite3.Error as e:
        print(f"Error adding review: {e}")
        return False  
    finally:
        if conn:
            conn.close()
            

if __name__ == "__main__":
    app.secret_key = "jfvdjhklvdfhgspierytuepsri5uw43hkjlh" 
    init_db()
    app.run(debug=True, port="9000")
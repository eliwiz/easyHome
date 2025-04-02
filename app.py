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

from database import init_db, reset_db
con = sqlite3.connect("database.db")
con.row_factory = sqlite3.Row

conn = sqlite3.connect('database.db')
# reset_db()
# init_db()

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

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'easyhomefdunoreply@gmail.com'
app.config['MAIL_PASSWORD'] = 'atod dhkj bwgp znig'  
app.config['MAIL_DEFAULT_SENDER'] = 'easyhomefdunoreply@gmail.com'
app.config['MAIL_DEBUG'] = True
mail = Mail(app)

#SQL3 databases do not work with UserMixin, *should* create temporary object in order for UserMixin to work properly
class User(UserMixin):
    def __init__(self, user_row):
        if user_row:  
            self.id = user_row["id"]
            self.first_name = user_row["first_name"]
            self.middle_name = user_row["middle_name"]
            self.last_name = user_row["last_name"]
            self.gender = user_row["gender"]
            self.phone_number = user_row["phone_number"]
            self.email = user_row["email"]
            self.password = user_row["password"]  
            self.street_name = user_row["street_name"]
            self.town = user_row["town"]
            self.state = user_row["state"]
            self.zip_code = user_row["zip_code"]

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

# @app.route("/admin", methods=["GET", "POST"])
# def admin():
#     list = get_all_users()
#     if request.method == "POST":
#         user_id = "delete_cart_item"
#         delete_user(user_id)
#     return render_template("admin.html", users=list)

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
        hourly = request.form.get("hourly")
        desc = request.form.get("desc")
        expertise = request.form.getlist("expertise[]")

        professions = ",".join(expertise)

        if password != password2:
            flash("Please make sure that your passwords match!", "warning")
            return redirect(url_for("registerProf"))
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        if c.fetchone() is not None:
            conn.close()
            flash("Email already registered!", "warning")
            return render_template("registerProf.html")
        conn.close()

        if add_prof(fname, mname, lname, gender, phone, email, password, apt, street, town, state, zip, professions, hourly, desc):
            flash("User registered successfully!", "success")
            return redirect(url_for("login"))
        else:
            flash("An error occurred while registering the user.", "danger")

        
    return render_template("registerProf.html")

#Professional pages (viewing as customer)
@app.route('/professionals', methods=["GET", "POST"])
def professionals():
    list = get_professionals()
    user_zip = None
    if current_user.is_authenticated:
        user_zip = get_user_by_id(current_user.id).zip_code
    
        
    if request.method == "POST":
        if "filters" in request.form:
            zip = request.form.get("zip_code")
            selected_distance = request.form.get("distance")
            expertise = request.form.getlist("expertise")
            print(expertise)
            
            if selected_distance != "0":
                upper = int(zip) + int(selected_distance)
                lower = int(zip) - int(selected_distance)
                list = get_profs_by_zip_range(int(lower), int(upper))
                
        if "name" in request.form:
            name = request.form.get("search")
            list = get_professionals_by_name(name)
            for prof in list:
                print(prof)
                
        
    return render_template("professionals.html", professionals=list, user_zip=user_zip)

@app.route('/createReservation/<profId>', methods=["GET", "POST"])
@login_required
def createReservation(profId):
    if request.method == "GET":
        professional = get_professional_by_id(profId)
        return render_template("createReservation.html", prof=professional)
    if request.method == "POST":
        prof_id = request.form.get("profID")
        title = request.form.get("title")
        description = request.form.get("desc")
        date = request.form.get('date')  # YYYY-MM-DD format (string)
        start = request.form.get('time')  # HH:MM format (string)
        hours = int(request.form.get('hour_amount'))   
        cost = request.form['cost']

        if add_work_detail(current_user.id, profId, title, description, cost, hours,date,start):
            msg = Message("You got a new Reservation!", recipients=[get_user_by_id(prof_id).email])
            msg.body = f"You just had a reservation booked by {get_user_by_id(current_user.id).first_name} {get_user_by_id(current_user.id).last_name}. \nThe project name is {title}, and it is on {date} which starts at {start}, and it {hours} long. It's decription is {description}. \n Log in to check it out and discuss with the client!"
            mail.send(msg)
            msg1 = Message("You booked a Reservation!", recipients=[get_user_by_id(current_user.id).email])
            msg1.body = f"You just booked a reservation with {get_user_by_id(prof_id).first_name} {get_user_by_id(prof_id).last_name}. \nThe project name is {title}, and it is on {date} which starts at {start}, and it {hours} long. It's decription is {description}. \n Your contractor will get in touch soon!"
            mail.send(msg1)
            flash("Reservation created sucessfully!", "success")
            return redirect(url_for("manageReservations"))
        else:
            flash("Error creating reservation", "danger")
        return url_for("professionals")

#Customer onlt pages (checking things they booked, updating info)
@app.route("/editUser", methods=["POST", "GET"])
@login_required
def editCustomer():
    print(current_user.id)
    userInformation = get_user_by_id(current_user.id)
    if request.method == "POST":
        if "general" in request.form:
            fname = request.form.get("fname")
            fname = request.form.get("fname")
            mname = request.form.get("mname")
            lname = request.form.get("lname")
            email = request.form.get("email")
            password = request.form.get("password")
            phone = request.form.get("phone")
            gender = request.form.get("gender")      
            apt = request.form.get("street/atp")
            street = request.form.get("street")
            town = request.form.get("town")
            state = request.form.get("state")
            zip = request.form.get("zip")
            if edit_user(current_user.id, fname, mname, lname, gender, phone, email, password, apt, street, town, state, zip):   
                flash("Sucessfully updated user details!", "success") 
                userInformation = get_user_by_id(current_user.id)
            else:
                flash("Error updating user details", "danger")
        if "work" in request.form:
            pass
    return render_template("editUser.html", userInfo= userInformation)

@app.route("/deleteUser", methods=["POST"])
@login_required
def deleteUser():
    if delete_user(current_user.id):
        flash("User sucessfully deleted", "success")
    else:
        flash("Error deleting user", "danger")
    return render_template("index.html")

@app.route("/manageReservations")
@login_required
def manageReservations():
    reserved = get_work_details_by_user(current_user.id)
    print(reserved)
    return render_template("manageReservations.html", reservations = reserved)

@app.route("/payReservation/<workID>", methods=["GET","POST"])
@login_required
def payReservation(workID):
    reservation = get_work_details_by_id(workID)
    if request.method=="GET":
        return render_template("payment.html", reserve = reservation)
    if request.method=="POST":
        edit_work_detail(reservation['work_id'], reservation['work_name'], reservation['work_description'], reservation['total_cost'], reservation['hour_amount'], reservation['date'], reservation['start_time'], 1)
        flash("Thank you for paying!","success")
        return redirect(url_for("manageReservations")) 
    
@app.route("/editReservation/<workID>", methods=["GET", "POST"])
@login_required
def editReservation(workID):
    reservation = get_work_details_by_id(workID)
    if request.method=="GET":
        return render_template("editReservation.html", reserve = reservation)
    if request.method=="POST":
        print("AH")
        title = request.form.get("title")
        description = request.form.get("desc")
        date = request.form.get('date')  # YYYY-MM-DD format (string)
        start = request.form.get('time')  # HH:MM format (string)

        edit_work_detail(reservation['work_id'], title, description, reservation['total_cost'], reservation['hour_amount'], date, start, reservation['is_paid'])
        flash("Successfully edited!","success")
        return redirect(url_for("manageReservations")) 

@app.route('/submit_review/<professional_id>', methods=["GET", "POST"])
@login_required
def submit_review(professional_id):
    if request.method == "POST":
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        
        # Validate the rating
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                flash("Rating must be between 1 and 5", "danger")
                return redirect(request.url)
        except ValueError:
            flash("Invalid rating value", "danger")
            return redirect(request.url)
        
        # Get the professional's user_id
        professional = get_professional_by_id(professional_id)
        if not professional:
            flash("Professional not found", "danger")
            return redirect(url_for('professionals'))
        
        # Add the review
        if add_review(current_user.id, professional_id, rating, comment):
            flash("Review submitted successfully", "success")
            return redirect(url_for('professionals'))
        else:
            flash("Failed to submit review", "danger")
            return redirect(request.url)
    
    # GET request - show the form
    professional = get_professional_by_id(professional_id)
    if not professional:
        flash("Professional not found", "danger")
        return redirect(url_for('professionals'))
    
    return render_template("submit_review.html", prof=professional)

@app.route('/reviews/<professional_id>')
def view_reviews(professional_id):
    try:
        professional = get_professional_by_id(professional_id)
        if not professional:
            flash("Professional not found", "danger")
            return redirect(url_for('professionals'))
            
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("""
            SELECT r.*, u.first_name, u.last_name
            FROM reviews r
            JOIN users u ON r.customer_id = u.id
            WHERE r.professional_id = ?
            ORDER BY r.id DESC
        """, (professional_id,))
        
        reviews = [dict(row) for row in c.fetchall()]
        return render_template('reviews.html', professional=professional, reviews=reviews)
    except sqlite3.Error as e:
        print(f"Error retrieving reviews: {e}")
        flash("An error occurred while retrieving reviews", "danger")
        return redirect(url_for('professionals'))
    finally:
        if conn:
            conn.close()

@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    reservation_id = request.form.get('reservation_id')  
    if reservation_id != None:
        if delete_work_detail(reservation_id):
            flash("Sucessfully cancelled reservation", "success")
        else:
            flash("There was an error trying to delete the reservation", "danger")
        return redirect(url_for('manageReservations')) 
    flash("Need user parameter, please cancel in your 'Manage Reservations' page", "warning") 
    return render_template("index.html")

#Unimportant pages, likely to get cut at end
@app.route('/full', methods=["GET", "POST"])
def indexfull():
    return render_template("index_full.html")

@app.route('/test')
def test():
    flash("This is a popup alert!", "prompt")  # Sending a message
    return render_template("test.html")

#FUNCTIONS
def get_professional_by_id(professional_id):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("""
            SELECT professionals.*, users.*
            FROM professionals
            JOIN users ON professionals.user_id = users.id
            WHERE professionals.id = ?
        """, (professional_id,))
        
        row = c.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Error retrieving professional: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_professional_rating(professional_id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT AVG(rating) as avg_rating 
            FROM reviews 
            WHERE professional_id = ?
        """, (professional_id,))
        
        result = c.fetchone()
        return round(result[0], 1) if result[0] is not None else "No ratings"
    except sqlite3.Error as e:
        print(f"Error getting rating: {e}")
        return "Error"
    finally:
        if conn:
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
        
        # Get professionals with their details
        c.execute("""
            SELECT u.id as user_id, u.first_name, u.last_name, u.town, u.zip_code, 
                   p.id as prof_id, p.profession, p.hourly_cost, p.description
            FROM users u
            JOIN professionals p ON u.id = p.user_id
            WHERE u.user_type = 'professional'
        """)
        professionals = [dict(row) for row in c.fetchall()]
        
        # Add ratings for each professional
        for prof in professionals:
            c.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(id) as review_count
                FROM reviews
                WHERE professional_id = ?
            """, (prof['prof_id'],))
            
            rating_data = c.fetchone()
            if rating_data:
                prof['avg_rating'] = round(rating_data['avg_rating'], 1) if rating_data['avg_rating'] else 0
                prof['review_count'] = rating_data['review_count']
            else:
                prof['avg_rating'] = 0
                prof['review_count'] = 0
                
        return professionals
    except sqlite3.Error as e:
        print(f"Error retrieving professionals: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_professionals_by_name(name):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        query = """
            SELECT u.id as user_id, u.first_name, u.last_name, u.town, u.zip_code, 
                   p.id as prof_id, p.profession, p.hourly_cost, p.description
            FROM users u
            JOIN professionals p ON u.id = p.user_id
            WHERE u.user_type = 'professional' AND (u.first_name LIKE ? OR u.middle_name LIKE ? OR u.last_name LIKE ?);
        """
        
        search_param = f"%{name}%"
        c.execute(query, (search_param, search_param, search_param))
        results = [dict(row) for row in c.fetchall()]
        
        for prof in results:
            c.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(id) as review_count
                FROM reviews
                WHERE professional_id = ?
            """, (prof['prof_id'],))
            
            rating_data = c.fetchone()
            if rating_data:
                prof['avg_rating'] = round(rating_data['avg_rating'], 1) if rating_data['avg_rating'] else 0
                prof['review_count'] = rating_data['review_count']
            else:
                prof['avg_rating'] = 0
                prof['review_count'] = 0
                
        return results
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    
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

def get_profs_by_zip_range(lower, upper):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()

        c.execute("""
            SELECT u.id as user_id, u.first_name, u.last_name, u.town, u.zip_code, p.id as prof_id, p.profession, p.hourly_cost, p.description
            FROM users u
            JOIN professionals p ON u.id = p.user_id
            WHERE u.zip_code BETWEEN ? AND ?
            AND user_type = 'professional'
        """, (lower, upper))

        results = [dict(row) for row in c.fetchall()]

        for prof in results:
            c.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(id) as review_count
                FROM reviews
                WHERE professional_id = ?
            """, (prof['prof_id'],))
            
            rating_data = c.fetchone()
            if rating_data:
                prof['avg_rating'] = round(rating_data['avg_rating'], 1) if rating_data['avg_rating'] else 0
                prof['review_count'] = rating_data['review_count']
            else:
                prof['avg_rating'] = 0
                prof['review_count'] = 0
                
        return results
    

    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        return []
    
    finally:
        if conn:
            conn.close()

def get_work_details_by_id(work_id):
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row 
        c = conn.cursor()

        c.execute("""
            SELECT 
                id AS work_id, work_name, work_description,
                total_cost, hour_amount, date, start_time, is_paid
            FROM workDetails
            WHERE id = ?
        """, (work_id,))

        work_row = c.fetchone()  
        return dict(work_row) if work_row else None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        if conn:
            conn.close()
            
def get_work_details_by_user(user_id):
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row  # Enables column access by name
        c = conn.cursor()

        c.execute("""
            SELECT 
                wd.id AS work_id, wd.work_name, wd.work_description,
                wd.professional_id, wd.total_cost, wd.hour_amount, 
                wd.date, wd.start_time, wd.is_paid, 
                p.id AS professional_primary_key, p.profession, p.hourly_cost, p.description,
                u.id AS user_id, u.first_name, u.last_name, u.email, u.phone_number
            FROM workDetails wd
            JOIN professionals p ON wd.professional_id = p.id
            JOIN users u ON p.user_id = u.id  
            WHERE wd.user_id = ?
        """, (user_id,))

        work_rows = c.fetchall()  
        return work_rows
    
    except sqlite3.Error as e:
        print(f"Error fetching work details: {e}")
        return None
    
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
        return True  
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
        return False 
    finally:
        if conn:
            conn.close()

def add_work_detail(user_id, professional_id, work_name, work_description, 
                    total_cost=0, hour_amount=0, date=None, start_time=None, is_paid=False):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO workDetails (work_name, work_description, user_id, professional_id,
                                     total_cost, hour_amount, date, start_time, is_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (work_name, work_description, user_id, professional_id, 
              total_cost, hour_amount, date, start_time, is_paid))

        conn.commit()
        print("Work detail added successfully")
        return True

    except sqlite3.Error as e:
        print(f"Error adding work detail: {e}")
        return False

    finally:
        conn.close()

def add_prof(first_name, middle_name, last_name, gender, phone_number, email, password, street_number, street_name, town, state, zip_code, professions, hourly_cost, description, is_verified=0):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO users (first_name, middle_name, last_name, gender, phone_number, email, password, street_number, street_name, town, state, zip_code, user_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, middle_name, last_name, gender, phone_number, email, password, 
              street_number, street_name, town, state, zip_code, "professional"))
        
        user_id = c.lastrowid
        c.execute("""
            INSERT INTO professionals (user_id, profession, hourly_cost, description)
            VALUES (?, ?, ?, ?)
        """, (user_id, professions, 10.00, "this is a test"))

        conn.commit()

        print(f"Professional added successfully with ID {user_id}")
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

def edit_user(user_id, first_name, middle_name, last_name, gender, phone_number, email, password, street_number, street_name, town, state, zip_code):    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            UPDATE users 
            SET first_name = ?, middle_name = ?, last_name = ?, gender = ?, 
                phone_number = ?, email = ?, password = ?, 
                street_number = ?, street_name = ?, town = ?, state = ?, 
                zip_code = ?
            WHERE id = ?
        """, (first_name, middle_name, last_name, gender, phone_number, email, password, 
              street_number, street_name, town, state, zip_code, user_id))

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

def edit_work_detail(work_id, work_name, work_description, total_cost, hour_amount, date, start_time, is_paid):    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            UPDATE workDetails 
            SET work_name = ?, work_description = ?, total_cost = ?, 
                hour_amount = ?, date = ?, start_time = ?, is_paid = ?
            WHERE id = ?
        """, (work_name, work_description, total_cost, hour_amount, date, start_time, is_paid, work_id))

        conn.commit()

        if c.rowcount > 0:
            print(f"Work detail with ID {work_id} updated successfully")
            return True
        else:
            print(f"No work detail found with ID {work_id}")
            return False

    except sqlite3.Error as e:
        print(f"Error updating work detail: {e}")
        return False

    finally:
        if conn:
            conn.close()
            
def delete_work_detail(work_id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("DELETE FROM workDetails WHERE id = ?", (work_id,))
        conn.commit()

        if c.rowcount > 0:
            print(f"Record with ID {work_id} deleted successfully")
            return True
        else:
            print(f"No record found with ID {work_id}")
            return False
    except sqlite3.Error as e:
        print(f"Error deleting record: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.secret_key = "jfvdjhklvdfhgspierytuepsri5uw43hkjlh" 
    init_db()
    app.run(debug=True, port="9000")
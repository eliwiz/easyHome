#imports
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from markupsafe import Markup, escape
import os, io
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from flask_mail import Message
from flask_login import LoginManager, UserMixin
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import quote

from database import init_db, reset_db
con = sqlite3.connect("database.db")
con.row_factory = sqlite3.Row

conn = sqlite3.connect('database.db')
# reset_db()
# init_db()

c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()

# print("Existing tables:", tables)

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
    cart = session.get('cart', [])
    # print(cart)
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

    # Ensure session cart exists
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']  # Retrieve cart

    if request.method == "POST":
        if "filters" in request.form:
            zip = request.form.get("zip_code")
            selected_distance = request.form.get("distance")
            expertise = request.form.getlist("expertise")

            if selected_distance != "0":
                upper = int(zip) + int(selected_distance)
                lower = int(zip) - int(selected_distance)
                list = get_profs_by_zip_range(int(lower), int(upper))
                
        elif "name" in request.form:
            name = request.form.get("search")
            list = get_professionals_by_name(name)

        elif "delete_cart_item" in request.form:
            item_index = int(request.form.get('item_index'))
            cart.pop(item_index - 1)  # Modify cart
            session['cart'] = cart  # Reassign session data
            session.modified = True  # ✅ Tell Flask session changed
            flash("Item removed successfully", "success")

    return render_template("professionals.html", professionals=list, user_zip=user_zip, cart=cart)

@app.route('/createReservation/<profId>', methods=["GET", "POST"])
@login_required
def createReservation(profId):
    cart = session.get('cart', [])
    if request.method == "GET":
        professional = get_professional_by_id(profId)
        return render_template("createReservation.html", prof=professional)
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("desc")
        startDate = request.form.get('startDate')  # YYYY-MM-DD format (string)
        endDate = request.form.get('endDate')  # YYYY-MM-DD format (string)
        time = request.form.get('time')  # HH:MM format (string)
        hours = int(request.form.get('hour_amount')) 
        # print(hours)  
        cost = request.form['cost']
        name = request.form['profName']

        cart.append([profId, title, description, cost, hours, startDate, endDate, time, name])
        # print(cart)
        flash("Reservation added to cart!", "success")
        return redirect(url_for("professionals"))
            
@app.route("/manageReservations")
@login_required
def manageReservations():
    reserved = get_work_details_by_user(current_user.id)
    # print(reserved)
    return render_template("manageReservations.html", reservations = reserved)

@app.route("/checkout", methods=["GET","POST"])
@login_required
def checkout():
    cart = session.get('cart', [])
    if request.method=="GET":
        return render_template("checkout.html", cart=cart)
    if request.method=="POST":
        sentEmail = request.form.get('sendEmails')
        for item in cart:
            if add_work_detail(current_user.id, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]) and add_work_history(current_user.id, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]):
                if sentEmail == "on":
                    # msg = Message("You got a new Reservation!", recipients=[get_user_by_id(item[0]).email])
                    # msg.body = f"You just had a reservation booked by {get_user_by_id(current_user.id).first_name} {get_user_by_id(current_user.id).last_name}. \nThe project name is {item[1]}, and it is from {item[5]} to {item[6]}. It starts at {item[7]}, and it {items[4]} long. It's decription is {item[2]}. \n Log in to check it out and discuss with the client!"
                    # mail.send(msg)
                    start_date = datetime.strptime(f"{item[5]} {item[7]}", "%Y-%m-%d %H:%M")
                    duration_hours = int(item[4])
                    end_date = start_date + timedelta(hours=duration_hours)

                    # Format to Google Calendar format: YYYYMMDDTHHMMSSZ
                    start_str = start_date.strftime("%Y%m%dT%H%M%SZ")
                    end_str = end_date.strftime("%Y%m%dT%H%M%SZ")

                    event_title = f"Reservation: {item[1]}"
                    event_details = f"Project with {get_user_by_id(item[0])['first_name']} {get_user_by_id(item[0])['last_name']}. Description: {item[2]}"
                    calendar_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(event_title)}&dates={start_str}/{end_str}&details={quote(event_details)}"
                    
                    
                    msg1 = Message("You booked a Reservation!", recipients=[get_user_by_id(current_user.id).email])
                    msg1.body = (
                        f"You just booked a reservation with {get_user_by_id(item[0])['first_name']} {get_user_by_id(item[0])['last_name']}.\n"
                        f"The project name is {item[1]}, and it is from {item[5]} to {item[6]}. It starts at {item[7]}, and it's {item[4]} hour(s) long. "
                        f"Its description is: {item[2]}.\nYour contractor will get in touch soon!\n\n"
                        f"📅 Add to your calendar: {calendar_url}"
                    )
                    mail.send(msg1)
            else:
                flash("There was an error in booking these reservations", "warning")
                break
        session['cart'].clear()     
        
        flash("Thank you for your purchase!","success")
        return redirect(url_for("manageReservations")) 
    
@app.route("/editReservation/<workID>", methods=["GET", "POST"])
@login_required
def editReservation(workID):
    reservation = get_work_details_by_id(workID)
    if request.method=="GET":
        return render_template("editReservation.html", reserve = reservation)
    if request.method=="POST":
        # print("AH")
        title = request.form.get("title")
        description = request.form.get("desc")
        startDate = request.form.get('startDate')  # YYYY-MM-DD format (string)
        endDate = request.form.get('endDate')  # YYYY-MM-DD format (string)
        start = request.form.get('time')  # HH:MM format (string)

        edit_work_detail(reservation['work_id'], title, description, reservation['total_cost'], reservation['hour_amount'], startDate, endDate, start, reservation['is_paid'])
        flash("Successfully edited!","success")
        return redirect(url_for("manageReservations")) 

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

#Customer only pages (checking things they booked, updating info)
@app.route("/editUser", methods=["POST", "GET"])
@login_required
def editCustomer():
    # print(current_user.id)
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
            zip = request.form.get("zip_code")
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

#Review Pages
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
            
#reservation History pages

@app.route("/reservationHistory")
@login_required
def reservationHistory():
    reserved = get_work_history_by_user(current_user.id)
    return render_template("history.html", reservations = reserved)

#admin pages

@app.route("/allReservationHistory")
@login_required
def allReservationHistory():
    reserved = get_all_work_history()
    return render_template("adminHistory.html", reservations = reserved)


#FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#user table functions
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

#Professional Table Functions
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

#Work Details/Reservation Table
def get_work_details_by_id(work_id):
    """Fetch a specific work detail by its ID."""
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT 
                id AS work_id, work_name, work_description,
                total_cost, hour_amount, start_date, end_date, start_time, is_paid
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
    """Fetch all work details related to a specific user."""
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT 
                wd.id AS work_id, wd.work_name, wd.work_description,
                wd.professional_id, wd.total_cost, wd.hour_amount, 
                wd.start_date, wd.end_date, wd.start_time, wd.is_paid, 
                p.id AS professional_primary_key, p.profession, p.hourly_cost, p.description,
                u.id AS user_id, u.first_name, u.last_name, u.email, u.phone_number
            FROM workDetails wd
            JOIN professionals p ON wd.professional_id = p.id
            JOIN users u ON p.user_id = u.id  
            WHERE wd.user_id = ?
        """, (user_id,))

        work_rows = c.fetchall()
        return [dict(row) for row in work_rows] if work_rows else None

    except sqlite3.Error as e:
        print(f"Error fetching work details: {e}")
        return None

    finally:
        if conn:
            conn.close()


def add_work_detail(user_id, professional_id, work_name, work_description, 
                    total_cost, hour_amount, start_date, end_date, start_time, is_paid=True):
    """Add a new work detail entry."""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO workDetails (work_name, work_description, user_id, professional_id,
                                     total_cost, hour_amount, start_date, end_date, start_time, is_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (work_name, work_description, user_id, professional_id, 
              total_cost, hour_amount, start_date, end_date, start_time, is_paid))

        conn.commit()
        print("Work detail added successfully")
        return True

    except sqlite3.Error as e:
        print(f"Error adding work detail: {e}")
        return False

    finally:
        if conn:
            conn.close()
        

def edit_work_detail(work_id, work_name, work_description, total_cost, hour_amount, start_date, end_date, start_time, is_paid):
    """Update an existing work detail."""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            UPDATE workDetails 
            SET work_name = ?, work_description = ?, total_cost = ?, 
                hour_amount = ?, start_date = ?, end_date = ?, start_time = ?, is_paid = ?
            WHERE id = ?
        """, (work_name, work_description, total_cost, hour_amount, start_date, end_date, start_time, is_paid, work_id))

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
    """Delete a work detail entry."""
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
            
#workHistory Table Functions

def add_work_history(user_id, professional_id, work_name, work_description, 
                     total_cost, hour_amount, start_date, end_date, start_time, is_paid=True):
    """Add a new work history entry."""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            INSERT INTO workHistory (work_name, work_description, user_id, professional_id,
                                     total_cost, hour_amount, start_date, end_date, start_time, is_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (work_name, work_description, user_id, professional_id, 
              total_cost, hour_amount, start_date, end_date, start_time, is_paid))

        conn.commit()
        print("Work history added successfully")
        return True

    except sqlite3.Error as e:
        print(f"Error adding work history: {e}")
        return False

    finally:
        if conn:
            conn.close()

def get_work_history_by_user(user_id):
    """Fetch all work history records related to a specific user."""
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT 
                wh.id AS work_id, wh.work_name, wh.work_description,
                wh.professional_id, wh.total_cost, wh.hour_amount, 
                wh.start_date, wh.end_date, wh.start_time, wh.is_paid, 
                p.id AS professional_primary_key, p.profession, p.hourly_cost, p.description,
                u.id AS user_id, u.first_name, u.last_name, u.email, u.phone_number
            FROM workHistory wh
            JOIN professionals p ON wh.professional_id = p.id
            JOIN users u ON p.user_id = u.id  
            WHERE wh.user_id = ?
        """, (user_id,))

        work_rows = c.fetchall()
        return [dict(row) for row in work_rows] if work_rows else None

    except sqlite3.Error as e:
        print(f"Error fetching work history: {e}")
        return None

    finally:
        if conn:
            conn.close()

def get_all_work_history():
    """Fetch all work history records from the database."""
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row  # Enables dictionary-like access to rows
        c = conn.cursor()

        c.execute("""
            SELECT 
                wh.id AS work_id, wh.work_name, wh.work_description,
                wh.user_id, wh.professional_id, wh.total_cost, wh.hour_amount,
                wh.start_date, wh.end_date, wh.start_time, wh.is_paid,
                u.first_name AS user_first_name, u.last_name AS user_last_name,
                p.profession, p.hourly_cost
            FROM workHistory wh
            JOIN users u ON wh.user_id = u.id
            JOIN professionals p ON wh.professional_id = p.id
        """)

        rows = c.fetchall()
        return [dict(row) for row in rows] if rows else []

    except sqlite3.Error as e:
        print(f"Error fetching work history: {e}")
        return []

    finally:
        if conn:
            conn.close()

            
#Review Table                       
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
            
#admin account
def create_admin():
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Check if a user with a specific email or ID already exists
        c.execute("SELECT * FROM users WHERE id = 1")
        if c.fetchone():
            print("Default user already exists.")
            return

        # Create the default user with ID=1
        c.execute("""
            INSERT INTO users (first_name, middle_name, last_name, gender, phone_number, email, password, 
                               street_number, street_name, town, state, zip_code, user_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Admin", "Admin", "User", "O", "0000000000", "easyhomefdunoreply@gmail.com", "admin123",
              "1", "Admin Street", "AdminTown", "AA", "00000", "customer"))

        conn.commit()
        print("Default user created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating default user: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.secret_key = "jfvdjhklvdfhgspierytuepsri5uw43hkjlh" 
    init_db()
    create_admin()
    app.run(debug=True, port="9000")
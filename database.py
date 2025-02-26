import sqlite3

def init_db():
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name VARCHAR2(25) NOT NULL,
                middle_name VARCHAR2(15),
                last_name VARCHAR2(25) NOT NULL,
                gender CHAR(1) CHECK (gender IN ('M','F','O')) NOT NULL,
                phone_number VARCHAR2(12) NOT NULL,
                email VARCHAR2(50) NOT NULL,
                password VARCHAR2(50) NOT NULL,
                street_number VARCHAR2(10),
                street_name VARCHAR2(35),
                town VARCHAR2(30),
                state CHAR(2),
                zip_code NUMBER(5)
                user_type VARCHAR2(20) CHECK (user_type IN ('customer','professional')) DEFAULT 'customer'
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS professionals (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  profession VARCHAR2(50) NOT NULL,
                  profession VARCHAR2(50) NOT NULL,
                  hourly_cost DECIMAL(10,2),
                  description TEXT,
                  is_verified BOOLEAN DEFAULT 0,
                  FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_id INTEGER NOT NULL,
                  professional_id INTEGER NOT NULL,
                  rating INTEGER CHECK(rating BETWEEN 1 AND 5) NOT NULL,
                  comment TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id),
                  FOREIGN KEY (professional_id) REFERENCES professionals(id)
            )
        """)

        conn.commit()
        print("Database initialization successful")
    
    except sqlite3.Error as e:
        print(f"Database Initialization error: {e}")
    
    finally:
        if conn:
            conn.close()

def reset_db():
    try: 
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS users')

        conn.commit()
        print("Database reset successfully")

    except sqlite3.Error as e:
        print(f"Database reset error: {e}")

    finally:
        if conn:
            conn.close()
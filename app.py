from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
import json
app = Flask(__name__)
dbconfig = json.load(open("dbconfig.json"))
db = mysql.connector.connect(host=dbconfig['host'], user=dbconfig['user'],
                             password=dbconfig['password'], database=dbconfig['database'])


@app.route("/")
def public():
    scity = request.args.get('scity')
    dcity = request.args.get('dcity')
    date_search = request.args.get('date_search')
    flight_num = request.args.get('flight_num')
    dateof = request.args.get('dateof')
    date_check = request.args.get('date_check')
    flights = None
    statuses = None
    cursor = db.cursor()
    if scity:
        query = """select * from flight, airport a1, airport a2
				where departure_airport = a1.airport_name and a1.airport_city = '{}'
				and arrival_airport = a2.airport_name and a2.airport_city = '{}'
				and departure_time LIKE '{}%' and status = 'upcoming'"""
        cursor.execute(query.format(scity, dcity, date_search))
        flights = cursor.fetchall()
    if flight_num:
        query = """select status from flight
				where flight_num = '{}' and {}_time LIKE '{}%'"""
        cursor.execute(query.format(flight_num, dateof, date_check))
        statuses = cursor.fetchall()
    cursor.close()
    return render_template('public.html', flights=flights, statuses=statuses)


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/register")
def signup():
    return render_template('register.html')


@app.route('/login_c')
def login_c():
    return render_template('login_c.html')


@app.route('/login_s')
def login_s():
    return render_template('login_s.html')


@app.route('/login_b')
def login_b():
    return render_template('login_b.html')


@app.route("/register_c")
def register_c():
    return render_template('register_c.html')


@app.route("/register_s")
def register_s():
    return render_template('register_s.html')


@app.route("/register_b")
def register_b():
    return render_template('register_b.html')

# Authenticates the login Customer


@app.route('/loginAuthC', methods=['GET', 'POST'])
def loginAuthC():
    # grabs information from the forms
    username = request.form['email']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM customer WHERE email = \'{}\' and password = \'{}\'"
    cursor.execute(query.format(username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        return redirect(url_for('public'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

# Authenticates the login Booking Agent


@app.route('/loginAuthB', methods=['GET', 'POST'])
def loginAuthB():
    # grabs information from the forms
    username = request.form['email']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM booking_agent WHERE email = \'{}\' and password = \'{}\'"
    cursor.execute(query.format(username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        return redirect(url_for('public'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

# Authenticates the login Airline Staff


@app.route('/loginAuthS', methods=['GET', 'POST'])
def loginAuthS():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM airline_staff WHERE username = \'{}\' and password = \'{}\'"
    cursor.execute(query.format(username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        return redirect(url_for('public'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)


# Authenticates the register Customer
@app.route('/registerAuthC', methods=['GET', 'POST'])
def registerAuthC():
    # grabs information from the forms
    email = request.form["email"]
    username = request.form['username']
    password = request.form['password']
    building_number = request.form["building_number"]
    street = request.form["street"]
    city = request.form["city"]
    state = request.form["state"]
    phone_number = request.form["phone_number"]
    passport_number = request.form["passport_number"]
    passport_expiration = request.form["passport_expiration"]
    passport_country = request.form["passport_country"]
    date_of_birth = request.form["date_of_birth"]

#	if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM customer WHERE email = \'{}\'"
    cursor.execute(query.format(username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO customer VALUES(\'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\')"
        cursor.execute(ins.format(email, username, password, building_number, street, city, state,
                                  phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return render_template('index.html')

# Authenticates the register Booking Agent


@app.route('/registerAuthB', methods=['GET', 'POST'])
def registerAuthB():
    # grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    booking_agent_id = request.form['booking_agent_id']

#	if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM booking_agent WHERE email= \'{}\'"
    cursor.execute(query.format(email))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO booking_agent VALUES(\'{}\', \'{}\',\'{}\')"
        cursor.execute(ins.format(email, password, booking_agent_id))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return render_template('index.html')

# Authenticates the register Airline Staff


@app.route('/registerAuthS', methods=['GET', 'POST'])
def registerAuthS():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form["last_name"]
    date_of_birth = request.form["date_of_birth"]
    airline_name = request.form["airline_name"]

#	if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = "SELECT * FROM airline_staff WHERE username = \'{}\'"
    cursor.execute(query.format(username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO airline_staff VALUES(\'{}\', \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')"
        cursor.execute(ins.format(username, password, first_name,
                                  last_name, date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        flash("You are logged in")
        return render_template('index.html')

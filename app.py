from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
import json
import datetime
import calendar
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
import os
import glob
import numpy as np
import random
import hashlib
import requests
mpl.use('Agg')
# mpl.is_interactive()
app = Flask(__name__)
dbconfig = json.load(open("dbconfig.json"))
conn = mysql.connector.connect(host=dbconfig['host'], user=dbconfig['user'],
                               password=dbconfig['password'], database=dbconfig['database'])

RECAPTCHA_SECRET = "6LcI1MwaAAAAAPC-dkPjZpT9b-vVko80g7EtXoRz"

def decode_2d(res):
    if not res:
        return res
    if len(res) == 1 and not res[0]:
        return res
    temp = []
    for i in res:
        temp1 = []
        for j in i:
            try:
                temp1.append(j.decode())
            except:
                temp1.append(j)
        temp.append(temp1)
    return temp

def decode_1d(res):
    if not res:
        return res
    temp = []
    for i in res:
        try:
            temp.append(i.decode())
        except:
            temp.append(i)
    return temp


def get_md5(s):
    md = hashlib.md5()
    md.update(s.encode('utf-8'))
    return md.hexdigest()


@app.route("/")
def public():
    stype = request.args.get('stype')
    dtype = request.args.get('dtype')
    src = request.args.get('src')
    dst = request.args.get('dst')
    date_search = request.args.get('date_search')
    flight_num = request.args.get('flight_num')
    datetype = request.args.get('datetype')
    date_check = request.args.get('date_check')
    flights = None
    statuses = None
    cursor = conn.cursor(prepared=True)
    if src:
        if stype == "city" and dtype == "city":
            query = """select * from flight, airport a1, airport a2
                    where departure_airport = a1.airport_name and a1.airport_city = %s
                    and arrival_airport = a2.airport_name and a2.airport_city = %s
                    and departure_time LIKE %s and status = 'upcoming'"""
        elif stype == "airport" and dtype == "city":
            query = """select * from flight, airport
                    where departure_airport = %s
                    and arrival_airport = airport.airport_name and airport.airport_city = %s
                    and departure_time LIKE %s and status = 'upcoming'"""
        elif stype == "city" and dtype == "airport":
            query = """select * from flight, airport
                    where departure_airport = airport.airport_name and airport.airport_city = %s
                    and arrival_airport = %s
                    and departure_time LIKE %s and status = 'upcoming'"""
        else:
            query = """select * from flight
                    where departure_airport = %s
                    and arrival_airport = %s
                    and departure_time LIKE %s and status = 'upcoming'"""
        cursor.execute(query, (src, dst, date_search+'%'))
        flights = decode_2d(cursor.fetchall())
        flights = decode_2d(flights)
    if flight_num:
        if datetype == "departure":
            query = """select status from flight
                    where flight_num = %s and departure_time LIKE %s"""
        elif datetype == "arrival":
            query = """select status from flight
                    where flight_num = %s and arrival_time LIKE %s"""
        else:
            return "illegal inputs"
        cursor.execute(query,(flight_num, date_check+'%'))
        statuses = cursor.fetchall()
        statuses = decode_2d(statuses)[0]
    cursor.close()
    kwargs = dict(
        stype=stype,
        dtype=dtype,
        src=src,
        dst=dst,
        date_search=date_search,
        flight_num=flight_num,
        datetype=datetype,
        date_check=date_check
    )
    for k, v in kwargs.items():
        if v == None:
            kwargs[k] = ""
    if "usertype" not in session:
        usertype = ""
    else:
        usertype = session["usertype"]
    return render_template('public.html', **kwargs, flights=flights, statuses=statuses, usertype=usertype)


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

    password = get_md5(password+"SSC")

    # cursor used to send queries
    cursor = conn.cursor(prepared=True)
    # executes query
    query = "SELECT * FROM customer WHERE email = %s and password = %s"
    cursor.execute(query, (username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    data = decode_1d(data)

    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        # creates a session for the the user
        # session is a built in
        name = data[1]
        session['username'] = name
        session['usertype'] = "customer"
        return redirect(url_for('customer_page'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login_c.html', error=error)

# Authenticates the login Booking Agent


@app.route('/loginAuthB', methods=['GET', 'POST'])
def loginAuthB():
    # grabs information from the forms
    username = request.form['email']
    password = request.form['password']
    password = get_md5(password+"SSC")
    # cursor used to send queries
    cursor = conn.cursor(prepared=True)
    # executes query
    query = "SELECT * FROM booking_agent WHERE email = %s and password = %s"
    cursor.execute(query,(username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    data = decode_1d(data)
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        session['usertype'] = "booking agent"
        return redirect(url_for('booking_agent_page'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login_b.html', error=error)

# Authenticates the login Airline Staff


@app.route('/loginAuthS', methods=['GET', 'POST'])
def loginAuthS():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    password = get_md5(password+"SSC")
    # cursor used to send queries
    cursor = conn.cursor(prepared=True)
    # executes query
    query = "SELECT * FROM airline_staff WHERE username = %s and password = %s"
    cursor.execute(query,(username, password))
    # stores the results in a variable
    profile = decode_1d(cursor.fetchone())
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(profile):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        session['usertype'] = "staff"

        # get this user's airline name
        cursor = conn.cursor(prepared=True)
        query = """select distinct airline_name from airline_staff
                    where username=%s"""
        cursor.execute(query,(username,))
        session['airline_name'] = decode_1d(cursor.fetchone())[0]
        cursor.close()
        return redirect(url_for('homeS'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login_s.html', error=error)


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

#   if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)

    password = get_md5(password+"SSC")

    # cursor used to send queries
    cursor = conn.cursor(prepared=True)
    # executes query
    query = "SELECT * FROM customer WHERE email = %s"
    cursor.execute(query,(username,))
    # stores the results in a variable
    data = decode_1d(cursor.fetchone())
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO customer VALUES(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(ins,(email, username, password, building_number, street, city, state,
                                  phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        session["username"] = username
        session["usertype"] = "customer"
        return redirect(url_for('customer_page'))

# Authenticates the register Booking Agent


@app.route('/registerAuthB', methods=['GET', 'POST'])
def registerAuthB():
    # grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    booking_agent_id = request.form['booking_agent_id']

#   if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)
    password = get_md5(password+"SSC")
    # cursor used to send queries
    cursor = conn.cursor(prepared=True)
    # executes query
    query = "SELECT * FROM booking_agent WHERE email= %s"
    cursor.execute(query,(email,))
    # stores the results in a variable
    data = decode_1d(cursor.fetchone())
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO booking_agent VALUES(%s,%s,%s)"
        cursor.execute(ins,(email, password, booking_agent_id))
        conn.commit()
        cursor.close()
        session["username"] = email
        session["usertype"] = "booking agent"
        return redirect(url_for('booking_agent_page'))

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
    recap = request.form["g-recaptcha-response"]
    data = {"secret": RECAPTCHA_SECRET,
            "response": recap}
    url = "https://www.google.com/recaptcha/api/siteverify"
    response = requests.post(url, data)
    response = requests.models.Response.json(response)
    if not response["success"]:
        error = "reCAPTCHA test failed"
        return render_template('register.html', error=error)
#   if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)
    password = get_md5(password+"SSC")
    # cursor used to send queries
    cursor = conn.cursor(prepared=True)
    # executes query
    query = "SELECT * FROM airline_staff WHERE username = %s"
    cursor.execute(query,(username,))
    # stores the results in a variable
    data = cursor.fetchone()
    data = decode_1d(data)
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = "INSERT INTO airline_staff VALUES(%s,%s,%s,%s,%s,%s)"
        cursor.execute(ins,(username, password, first_name,
                                  last_name, date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        session["username"] = username
        session["usertype"] = "staff"
        session["airline_name"] = airline_name
        return redirect(url_for('homeS'))


@app.route("/homeS")
def homeS():
    if "username" in session:
        return render_template('home_s.html')
    else:
        return redirect(url_for('public'))



@app.route('/logout')
def logout():
    try:
        session.pop('username')
        session.pop('usertype')
        session.pop('airline_name')
    except KeyError:
        pass
    return redirect('/')


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


@app.route("/staff_view_my_flights")
def staff_view_my_flights():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    stype = request.args.get('stype')
    dtype = request.args.get('dtype')
    src = request.args.get('src')
    dst = request.args.get('dst')
    flights = None
    if not start_date:
        start_date = datetime.datetime.today().strftime('%Y-%m-%d')
        end_date = add_months(datetime.date.today(), 1).strftime('%Y-%m-%d')

    airline_name = session["airline_name"]
    cursor = conn.cursor(prepared=True)
    if not (src or dst):
        query = """select * from flight
                where departure_time between %s and %s
                and airline_name=%s"""
        cursor.execute(query,(start_date+' 00:00:00', end_date+' 00:00:00', airline_name))
    elif src and (not dst):
        if stype == "airport":
            query = """select * from flight
                    where departure_time between %s and %s
                    and departure_airport = %s
                    and airline_name=%s"""
        else:
            query = """select flight.* from flight, airport
                    where departure_time between %s and %s
                    and airport_city = %s
                    and departure_airport = airport_name
                    and airline_name=%s"""
        cursor.execute(query,(start_date+' 00:00:00', end_date+' 00:00:00', src, airline_name))
    elif (not src) and dst:
        if dtype == "airport":
            query = """select * from flight
                    where departure_time between %s and %s
                    and arrival_airport = %s
                    and airline_name=%s"""
        else:
            query = """select flight.* from flight, airport
                    where departure_time between %s and %s
                    and airport_city = %s
                    and arrival_airport = airport_name
                    and airline_name=%s"""
        cursor.execute(query,(start_date+' 00:00:00', end_date+' 00:00:00', dst, airline_name))
    else:
        if stype == "airport" and dtype == "airport":
            query = """select * from flight
                    where departure_time between %s and %s
                    and departure_airport = %s
                    and arrival_airport = %s
                    and airline_name=%s"""
        elif stype == "city" and dtype == "airport":
            query = """select flight.* from flight, airport
                    where departure_time between %s and %s
                    and airport_city = %s
                    and arrival_airport = %s
                    and departure_airport = airport_name
                    and airline_name=%s"""
        elif stype == "airport" and dtype == "city":
            query = """select flight.* from flight, airport
                    where departure_time between %s and %s
                    and departure_airport = %s
                    and airport_city = %s
                    and arrival_airport = airport_name
                    and airline_name=%s"""
        else:
            query = """select flight.* from flight, airport a1, airport a2
                    where departure_time between %s and %s
                    and a1.airport_city = %s
                    and a2.airport_city = %s
                    and departure_airport = a1.airport_name
                    and arrival_airport = a2.airport_name
                    and airline_name=%s"""
        cursor.execute(query,(
            start_date+' 00:00:00', end_date+' 00:00:00', src, dst, airline_name))

    flights = decode_2d(cursor.fetchall())
    cursor.close()
    flights = [list(x) for x in flights]
    for i, flight in enumerate(flights):
        for j, attribute in enumerate(flight):
            flights[i][j] = str(flights[i][j])
    kwargs = dict(
        start_date=start_date,
        end_date=end_date,
        stype=stype,
        dtype=dtype,
        src=src,
        dst=dst,
        flights=flights
    )
    for k, v in kwargs.items():
        if v == None:
            kwargs[k] = ""
    return render_template("staff_view_my_flights.html", **kwargs)


@app.route("/view_customers")
def view_customers():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    flight_num = request.args.get("flight_num")
    cursor = conn.cursor(prepared=True)
    query = """select distinct customer.* from purchases, ticket, customer
            where flight_num = %s
            and email = customer_email
            and purchases.ticket_id = ticket.ticket_id
            """
    cursor.execute(query,(flight_num,))
    customers = decode_2d(cursor.fetchall())
    cursor.close()
    customers = [[str(x) for x in row] for row in customers]
    # customers = json.dumps(customers)
    # remove password
    for i in range(len(customers)):
        del customers[i][2]
    kwargs = dict(
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date"),
        stype=request.args.get('stype'),
        dtype=request.args.get('dtype'),
        src=request.args.get('src'),
        dst=request.args.get('dst'),
        customers=customers
    )
    return render_template("staff_view_customers.html", **kwargs)


@app.route("/staff_create_new_flights")
def staff_create_new_flights():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    flight_num = request.args.get("flight_num")
    if not flight_num:
        return render_template("staff_create_new_flights.html", res=None)
    departure_airport = request.args.get("departure_airport")
    departure_time = request.args.get("departure_time").replace("T", " ")
    arrival_airport = request.args.get("arrival_airport")
    arrival_time = request.args.get("arrival_time").replace("T", " ")
    price = request.args.get("price")
    status = request.args.get("status")
    airplane_id = request.args.get("airplane_id")

    cursor = conn.cursor(prepared=True)
    query = """insert into flight values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    try:
        cursor.execute(query,(session["airline_name"],
                                    flight_num,
                                    departure_airport,
                                    departure_time,
                                    arrival_airport,
                                    arrival_time,
                                    price,
                                    status,
                                    airplane_id))
        conn.commit()
        res = flight_num
    except Exception as e:
        # return str(e)
        res = "error"
    cursor.close()

    return render_template("staff_create_new_flights.html", res=res)


@ app.route("/staff_change_flights_status")
def staff_change_flights_status():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    flight_num = request.args.get("flight_num")
    if not flight_num:
        return render_template("staff_change_flights_status.html", res=None)
    status = request.args.get("status")

    cursor = conn.cursor(prepared=True)
    query = """select airline_name from flight
    where flight_num = %s"""
    cursor.execute(query,(flight_num,))
    flights = decode_2d(cursor.fetchall())
    if not flights:
        res = "notfound"
        cursor.close()
        return render_template("staff_change_flights_status.html", res=res)
    airline_name = flights[0][0]
    if airline_name != session["airline_name"]:
        res = "noaccess"
        cursor.close()
        return render_template("staff_change_flights_status.html", res=res)
    query = """update flight
                set status = %s
                where flight_num = %s
                and airline_name = %s"""
    try:
        cursor.execute(query,(status,
                                    flight_num,
                                    session["airline_name"]))
        conn.commit()
        res = flight_num
    except Exception as e:
        # return str(e)
        res = "error"
    cursor.close()

    return render_template("staff_change_flights_status.html", res=res)


@ app.route("/staff_add_airplane")
def staff_add_airplane():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    airplane_id = request.args.get("airplane_id")
    if not airplane_id:
        return render_template("staff_add_airplane.html", res=None)
    seats = request.args.get("seats")
    cursor = conn.cursor(prepared=True)
    query = """select * from airplane
    where airplane_id = %s
    and airline_name = %s"""
    cursor.execute(query,(airplane_id, session["airline_name"]))
    airplanes = decode_2d(cursor.fetchall())
    if airplanes:
        cursor.close()
        return render_template("staff_add_airplane.html", res="exist")
    query = """insert into airplane values (%s, %s, %s)"""
    try:
        cursor.execute(query,(
            session["airline_name"], airplane_id, seats))
        conn.commit()
        res = airplane_id
    except Exception as e:
        # return str(e)
        res = "error"
    cursor.close()
    return render_template("staff_add_airplane.html", res=res)


@ app.route("/staff_add_airport")
def staff_add_airport():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    airport_name = request.args.get("airport_name")
    if not airport_name:
        return render_template("staff_add_airport.html", res=None)
    airport_city = request.args.get("airport_city")
    cursor = conn.cursor(prepared=True)
    query = """select * from airport
    where airport_name = %s"""
    cursor.execute(query,(airport_name,))
    airports = decode_2d(cursor.fetchall())
    if airports:
        cursor.close()
        return render_template("staff_add_airport.html", res="exist")
    query = """insert into airport values (%s, %s)"""
    try:
        cursor.execute(query,(airport_name, airport_city))
        conn.commit()
        res = airport_name
    except Exception as e:
        # return str(e)
        res = "error"
    cursor.close()
    return render_template("staff_add_airport.html", res=res)


@ app.route("/staff_view_booking_agents")
def staff_view_booking_agents():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    cursor = conn.cursor(prepared=True)
    query = """select booking_agent.*, count(*)
            from booking_agent natural join purchases natural join ticket
            where purchase_date > %s
            and airline_name = %s
            group by email
            order by count(*) DESC
            limit 5
            """
    last_month = add_months(datetime.date.today(), -1).strftime('%Y-%m-%d')
    cursor.execute(query,(last_month, session["airline_name"]))
    data1 = decode_2d(cursor.fetchall())
    data1 = [[attr for attr in agent] for agent in data1]
    # remove password
    for i in range(len(data1)):
        del data1[i][1]

    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    cursor.execute(query,(last_year, session["airline_name"]))
    data2 = decode_2d(cursor.fetchall())
    data2 = [[attr for attr in agent] for agent in data2]
    # remove password
    for i in range(len(data2)):
        del data2[i][1]

    query = """select booking_agent.*, sum(price)*0.1
            from booking_agent natural join purchases natural join ticket natural join flight
            where purchase_date > %s
            and airline_name = %s
            group by email
            order by sum(price) DESC
            limit 5
            """
    cursor.execute(query,(last_year, session["airline_name"]))
    data3 = decode_2d(cursor.fetchall())
    data3 = [[attr for attr in agent] for agent in data3]
    # remove password
    for i in range(len(data3)):
        del data3[i][1]
    cursor.close()
    kwargs = dict(
        data1=data1,
        date1=last_month,
        data2=data2,
        date2=last_year,
        data3=data3,
        date3=last_year
    )
    return render_template("staff_view_booking_agents.html", **kwargs)


@ app.route("/staff_view_frequent_customers")
def staff_view_frequent_customers():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    cursor = conn.cursor(prepared=True)
    query = """
            select customer.*, count(*)
            from customer, purchases, ticket
            where customer.email = purchases.customer_email
            and ticket.ticket_id = purchases.ticket_id
            and airline_name = %s
            and purchase_date > %s
            group by email
            order by count(*) DESC
            limit 1
            """
    cursor.execute(query,(session["airline_name"], last_year))
    top_customer = decode_2d(cursor.fetchall())[0]
    top_customer = [str(attr) for attr in top_customer]
    del top_customer[2]

    email = request.args.get("email")
    query = """
            select distinct flight.*
            from flight natural join purchases natural join ticket
            where customer_email = %s
            and airline_name = %s
            """
    cursor.execute(query,(email, session["airline_name"]))
    flights = decode_2d(cursor.fetchall())
    flights = [[str(attr) for attr in flight] for flight in flights]

    cursor.close()
    kwargs = dict(
        top_customer=top_customer,
        last_year=last_year,
        my_airline=session["airline_name"],
        flights=flights,
        email=email
    )
    return render_template("staff_view_frequent_customers.html", **kwargs)


@ app.route("/staff_view_reports")
def staff_view_reports():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    cursor = conn.cursor(prepared=True)
    query = """
            select count(*)
            from purchases natural join ticket
            where airline_name = %s
            and purchase_date > %s
            and purchase_date < curdate()
            """
    cursor.execute(query,(session["airline_name"], last_year))
    amt_tck_ly = str(cursor.fetchall()[0][0])

    last_month = add_months(datetime.date.today(), -1).strftime('%Y-%m-%d')
    cursor.execute(query,(session["airline_name"], last_month))
    amt_tck_lm = str(cursor.fetchall()[0][0])

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    amt_tck_range = None
    if start_date:
        query = """
                select count(*)
                from purchases natural join ticket
                where airline_name = %s
                and (purchase_date between %s and %s)
                """
        cursor.execute(query,(
            session["airline_name"], start_date+' 00:00', end_date+' 23:59'))
        amt_tck_range = str(cursor.fetchall()[0][0])

    year = request.args.get("year")
    img_url = ""
    if year:
        # clear history images
        dir = './static/staff_view_reports/'
        filelist = glob.glob(os.path.join(dir, "*"))
        for f in filelist:
            os.remove(f)
        image_name = str(time.time()).split(
            '.')[-1] + '.png'  # avoid image caching
        img_url = os.path.join(dir, image_name)
        sales = []
        for month in range(1, 13):
            query = """
                    select count(*)
                    from purchases natural join ticket
                    where year(purchase_date) = %s
                    and month(purchase_date) = %s
                    and airline_name = %s
                    """
            cursor.execute(query,(year, month, session["airline_name"]))
            sales.append(int(cursor.fetchall()[0][0]))
        x = [m for m in range(1, 13)]
        fig, axes = plt.subplots(1, 1)
        axes.bar(x, sales)
        axes.xaxis.set_ticks(x)
        axes.set_title(f"Monthly sales in {year}")
        axes.set_xlabel("month")
        axes.set_ylabel("sales")
        plt.savefig(img_url)

    cursor.close()

    current_year = datetime.date.today().strftime('%Y-%m-%d')[:4]
    kwargs = dict(
        amt_tck_ly=amt_tck_ly,
        amt_tck_lm=amt_tck_lm,
        start_date=start_date,
        end_date=end_date,
        amt_tck_range=amt_tck_range,
        current_year=current_year,
        img_url=img_url,
        year=year
    )
    # return json.dumps(kwargs)
    return render_template("staff_view_reports.html", **kwargs)


@ app.route("/staff_compare_revenue")
def staff_compare_revenue():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    cursor = conn.cursor(prepared=True)
    query = """
            select sum(price)
            from purchases natural join ticket natural join flight
            where airline_name = %s
            and booking_agent_id {} NULL
            and purchase_date > %s
            """

    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    last_month = add_months(datetime.date.today(), -1).strftime('%Y-%m-%d')

    cursor.execute(query.format("is"),(session["airline_name"], last_year))
    res = decode_2d(cursor.fetchall())[0][0]
    direct_ly = 0 if not res else int(res)

    cursor.execute(query.format("is not"),(session["airline_name"], last_year))
    res = decode_2d(cursor.fetchall())[0][0]
    indirect_ly = 0 if not res else int(res)

    cursor.execute(query.format("is"),(session["airline_name"], last_month))
    res = decode_2d(cursor.fetchall())[0][0]
    direct_lm = 0 if not res else int(res)

    cursor.execute(query.format("is not"),(session["airline_name"], last_month))
    res = decode_2d(cursor.fetchall())[0][0]
    indirect_lm = 0 if not res else int(res)

    cursor.close()

    dir = './static/staff_compare_revenue/'
    filelist = glob.glob(os.path.join(dir, "*"))
    for f in filelist:
        os.remove(f)
    image_name = str(time.time()).split(
        '.')[-1] + '.png'  # avoid image caching
    img_url = os.path.join(dir, image_name)

    x1 = [direct_ly, indirect_ly]
    x2 = [direct_lm, indirect_lm]
    labels = ["direct_sales", "indirect_sales"]

    fig, axes = plt.subplots(2)

    def func(pct, allvals):
        absolute = int(pct/100.*np.sum(allvals))
        return "{:.1f}%\n({:d} $)".format(pct, absolute)


    wedges, texts, autotexts = axes[0].pie(x1, autopct=lambda pct: func(pct, x1),
                                  textprops=dict(color="w"))
    axes[0].legend(wedges, labels, loc=(1.0, 0.6))
    axes[0].set_title(f"Revenue comparison in last year")

    wedges, texts, autotexts = axes[1].pie(x2, autopct=lambda pct: func(pct, x2),
                                  textprops=dict(color="w"))
    axes[1].legend(wedges, labels, loc=(1.0, 0.6))
    axes[1].set_title(f"Revenue comparison in last month")
    plt.savefig(img_url)

    kwargs = dict(
        direct_ly=direct_ly,
        indirect_ly=indirect_ly,
        direct_lm=direct_lm,
        indirect_lm=indirect_lm,
        img_url=img_url
    )
    return render_template("staff_compare_revenue.html", **kwargs)


@ app.route("/staff_view_top_destinations")
def staff_view_top_destinations():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "staff":
        return redirect("/")
    cursor = conn.cursor(prepared=True)
    query = """
            select airport_city
            from (purchases natural join ticket natural join flight), airport
            where arrival_airport = airport_name
            and purchase_date > %s
            and airline_name = %s
            group by airport_city
            order by count(*)
            desc
            limit 3
            """
    last_year = add_months(datetime.date.today(), -12).strftime('%Y-%m-%d')
    last_3months = add_months(datetime.date.today(), -3).strftime('%Y-%m-%d')

    cursor.execute(query,(last_year, session["airline_name"]))
    dsts_ly = [row[0] for row in decode_2d(cursor.fetchall())]

    cursor.execute(query,(last_3months, session["airline_name"]))
    dsts_l3m = [row[0] for row in decode_2d(cursor.fetchall())]
    cursor.close()

    kwargs = dict(
        dsts_ly=dsts_ly,
        dsts_l3m=dsts_l3m
        )
    return render_template("staff_view_top_destinations.html", **kwargs)

@ app.route("/show_sessions")
def show_sessions():
    d = {}
    for k, v in session.items():
        d[k] = v
    return json.dumps(d)


@app.route('/customer_page')
def customer_page():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "customer":
        return redirect("/")
    if "username" in session:
        username = session["username"]
        return render_template("/customer_page.html", username = "Welcome! "+username, flights_rec = None, flights_found = None)
    else:
        return redirect(url_for('public'))

@app.route('/booking_agent_page')
def booking_agent_page():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "booking agent":
        return redirect("/")
    if "username" in session:
        username = session["username"]
        return render_template("/booking_agent_page.html", username = "Welcome! "+username, flights_rec = None, flights_found = None)
    else:
        return redirect(url_for('public'))

@app.route('/view_my_flights', methods = ["GET", "POST"])
def view_my_flights():
    usertype = session["usertype"]
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] == "staff":
        return redirect("/")
    cursor = conn.cursor(prepared=True)
    choice = request.form["choice"]
    if choice == "default":
        out = None
        # cursor used to send queries
        print(session["username"])
        # executes query
        if usertype == "customer":
            query = "SELECT * FROM flight where status = 'upcoming' and flight_num in (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN customer WHERE name =%s)"
        elif usertype == "booking agent":
            query = "SELECT * FROM flight where status = 'upcoming' and flight_num in (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE email =%s)"
        elif usertype == "staff":
            query = "SELECT * FROM flight where status = 'upcoming' and airline_name = (SELECT airline_name FROM airline_staff WHERE username = %s) and DateDiff(departure_time, CURDATE()) <= 30"
        cursor.execute(query,(session["username"],))
        # stores the results in a variable
        out = decode_2d(cursor.fetchall())
        # use fetchall() if you are expecting more than 1 data row
    elif choice == "specify":
        info = request.form.getlist("info")
        cities = "SELECT airport_city FROM airport"
        cursor.execute(cities)
        res = decode_2d(cursor.fetchall())
        city = []
        for i in res:
            city.append(i[0])
        airports = "SELECT airport_name FROM airport"
        cursor.execute(airports)
        out = decode_2d(cursor.fetchall())
        airport = []
        for i in out:
            airport.append(i[0])

        place = None
        time = None

        out = []
        data1 = []
        data2 = []

        for i in info:
            if i == "date":
                time = i
            elif i == "name":
                place = i

        if time is not None:
            start = request.form["start"]
            end = request.form["end"]
            if usertype == "customer":
                query1 = "SELECT * FROM flight WHERE (departure_time between%s and%s) and flight_num in (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN customer WHERE name =%s)"
            elif usertype == "booking agent":
                query1 = "SELECT * FROM flight WHERE (departure_time between%s and%s) and flight_num in (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE email =%s)"
            elif usertype == "staff":
                query1 = "SELECT * FROM flight WHERE (departure_time between%s and%s) and airline_name = (SELECT airline_name FROM airline_staff WHERE username =%s)"
            cursor.execute(query1,(start,end,session["username"]))
            data1 = decode_2d(cursor.fetchall())

        if place is not None:
            dept = request.form["d_name"]
            arr = request.form["a_name"]
            if dept in city and arr in city:
                if usertype == "customer":
                    query2 = "SELECT * FROM flight WHERE departure_airport in (SELECT airport_name FROM airport \
                        WHERE airport_city =%s) and arrival_airport in (select airport_name from airport where airport_city =%s) and flight_num in \
                        (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN customer WHERE name =%s)"
                elif usertype == "booking agent":
                    query2 = "SELECT * FROM flight WHERE departure_airport in (SELECT airport_name FROM airport \
                        WHERE airport_city =%s) and arrival_airport in (select airport_name from airport where airport_city =%s) and flight_num in \
                        (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE email =%s)"
                elif usertype == "staff":
                    query2 = "SELECT * FROM flight WHERE departure_airport in (SELECT airport_name FROM airport \
                        WHERE airport_city =%s) and arrival_airport in (select airport_name from airport where airport_city =%s) and airline_name = \
                        (SELECT airline_name FROM airline_staff WHERE username =%s)"
                cursor.execute(query2,(dept,arr,session["username"]))
                data2 = decode_2d(cursor.fetchall())
            elif dept in airport and arr in airport:
                if usertype == "customer":
                    query2 = "SELECT * FROM flight WHERE departure_airport =%s and arrival_airport =%s and flight_num in\
                            (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN customer WHERE name =%s)"
                elif usertype == "booking agent":
                    query2 = "SELECT * FROM flight WHERE departure_airport =%s and arrival_airport =%s and flight_num in\
                        (SELECT flight_num FROM purchases NATURAL JOIN ticket NATURAL JOIN booking_agent WHERE email =%s)"
                elif usertype == "staff":
                    query2 = "SELECT * FROM flight WHERE departure_airport =%s and arrival_airport =%s and airline_name =\
                        (SELECT airline_name FROM airline_staff WHERE username =%s)"
                cursor.execute(query2,(dept,arr,session["username"]))
                data2 = decode_2d(cursor.fetchall())
        if data1 == [] and data2 == []:
            out = []
        elif data1 != [] and data2 == []:
            out = data1
        elif data2 != [] and data1 == []:
            out = data2
        else:
            for i in data1:
                for i in data2:
                    out.append(i)
    cursor.close()
    if usertype == "customer":
        print(out)
        return render_template("customer_page.html", username = session["username"],flights_rec = out,flights_found=None)
    elif usertype == "booking agent":
        return render_template("booking_agent_page.html", username = session["username"],flights_rec = out,flight_found = None)

@app.route('/track_my_spending_c')
def track_my_spending_c():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "customer":
        return redirect("/")
    return render_template('track_my_spending_c.html')


@app.route('/spending_c', methods = ["GET", "POST"])
def spending_c():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "customer":
        return redirect("/")
    choice = request.form["choice"]
    cursor = conn.cursor(prepared=True)

    if choice == "default":
        year = "SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN customer WHERE name =%s\
            and DateDiff(CURDATE(), purchase_date) <= 365"
        cursor.execute(year,(session["username"],))
        spend = decode_1d(cursor.fetchone())[0]
        month = "SELECT SUM(price),convert(purchase_date, char(7)) FROM purchases NATURAL JOIN ticket NATURAL JOIN\
            flight NATURAL JOIN customer WHERE name =%s and DateDiff(CURDATE(), purchase_date) <= 365/2 and DateDiff(CURDATE(), purchase_date) >= 0 \
            GROUP BY convert(purchase_date, char(7))"
        cursor.execute(month,(session["username"],))
        spent = decode_2d(cursor.fetchall())

    elif choice == "specify":
        start = request.form["start"]
        end = request.form["end"]
        year = "SELECT SUM(price) FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN customer WHERE name =%s\
            and purchase_date between%s and%s"
        cursor.execute(year,(session["username"], start, end))
        spend = decode_1d(cursor.fetchone())[0]

        month = "SELECT SUM(price),convert(purchase_date, char(7)) FROM purchases NATURAL JOIN ticket NATURAL JOIN\
            flight NATURAL JOIN customer WHERE name =%s and purchase_date between%s and%s GROUP BY convert(purchase_date, char(7))"
        cursor.execute(month,(session["username"], start, end))
        spent = decode_2d(cursor.fetchall())
    spent.sort(key=lambda x: x[1])
    value = []
    label = []
    for i in spent:
        value.append(i[0])
        label.append(i[1])
    if len(value) >0:
        maxi = max(value)
    else:
        maxi = 100
    return render_template('track_my_spending_c.html', spending = spend, spent = spent, value = value, label = label,maxi = maxi)

@app.route("/purchase")
def purchase():
    if "usertype" not in session:
        return redirect("/")
    usertype = session["usertype"]
    username = session["username"]

    start_date = datetime.datetime.today().strftime('%Y-%m-%d')
    if session["usertype"] == "staff":
        return redirect("/")
    return render_template('purchase.html', username = username, usertype = usertype,today = start_date)

@app.route('/search_flights', methods = ["GET", "POST"])
def search_flights():
    if "usertype" not in session:
        return redirect("/")
    usertype = session["usertype"]
    if session["usertype"] == "staff":
        return redirect("/")
    scity = request.args.get('scity')
    dcity = request.args.get('dcity')
    sair = request.args.get("sair")
    dair = request.args.get("dair")
    date_search = request.args.get('date_search')
    flight_num = request.args.get('flight_num')
    dateof = request.args.get('dateof')
    date_check = request.args.get('date_check')
    flights = None
    statuses = None
    cursor = conn.cursor(prepared=True)

    start_date = datetime.datetime.today().strftime('%Y-%m-%d')
    # grab all cities in the database
    querycity = "SELECT airport_city from airport"
    cursor.execute(querycity)
    citiesdata = decode_2d(cursor.fetchall())
    cities = []
    for i in citiesdata:
        cities.append(i[0])
    # grab all airports in the database
    queryairport = "SELECT airport_name from airport"
    cursor.execute(queryairport)
    airportsdata = decode_2d(cursor.fetchall())
    airports = []
    for i in airportsdata:
        airports.append(i[0])

    error1 = None
    if scity:
        if (scity not in cities) or (dcity not in cities):
            error1 = "Errors in City names, please check again and enter a correct one"
            if usertype =="booking agent" or usertype == "customer":
                return render_template('purchase.html', error = error1)
        else:
            query = """select * from flight, airport a1, airport a2
                    where departure_airport = a1.airport_name and a1.airport_city = %s
                    and arrival_airport = a2.airport_name and a2.airport_city = %s
                    and departure_time LIKE %s and status = 'upcoming'"""
            cursor.execute(query,(scity, dcity, date_search+'%'))
            flights = decode_2d(cursor.fetchall())
    elif sair:
        if (sair not in airports) or (dair not in airports):
            error1 = "Errors in Airport names, please check again and enter a correct one"
            if usertype =="booking agent" or usertype == "customer":
                return render_template('purchase.html', error = error1)
        else:
            query = """select * from flight, airport a1, airport a2
                    where departure_airport = a1.airport_name and a1.airport_name = %s
                    and arrival_airport = a2.airport_name and a2.airport_name = %s
                    and departure_time LIKE %s and status = 'upcoming'"""
            cursor.execute(query,(sair, dair, date_search+'%'))
            flights = decode_2d(cursor.fetchall())
    elif flight_num:
        query = """select status from flight
                where flight_num = %s and {}_time LIKE %s"""
        cursor.execute(query,(flight_num, dateof, date_check+'%'))
        statuses = decode_2d(cursor.fetchall())
    conn.commit()
    cursor.close()
    air_name = []
    flight_num = []
    le = len(flights)
    for i in flights:
        air_name.append(i[0])
        flight_num.append(i[1])
    if usertype == "booking agent" or usertype == "customer":
        return render_template("purchase.html", flights = flights, statuses = statuses, air_name = air_name, flight_num = flight_num,length = le, today = start_date)




@app.route("/purchase_confirm")
def purchase_confirm():
    if "usertype" not in session:
        return redirect("/")
    usertype = session["usertype"]
    username = session["username"]
    if session["usertype"] == "staff":
        return redirect("/")
    return render_template('purchase_confirm.html', username = username, usertype = usertype)

@app.route('/purchasing', methods = ["GET", "POST"])
def purchasing():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] == "staff":
        return redirect("/")
    airline_name = request.form["airline_name"]
    flight_num = request.form["flight_num"]
    usertype = session["usertype"]
    message1 = None
    session["airline_name"] = airline_name
    session["flight_num"] = flight_num
    cursor = conn.cursor(prepared=True)

    # check whether the seats of the plane is enough.
    seatcount = "SELECT seats FROM airplane NATURAL JOIN flight WHERE flight.airline_name =%s and flight.flight_num =%s"
    cursor.execute(seatcount,(airline_name, flight_num))
    seat = decode_1d(cursor.fetchone())
    print(seat[0])

    ticketcount = "SELECT count(*) FROM ticket WHERE airline_name =%s and flight_num =%s"
    cursor.execute(ticketcount,(airline_name, flight_num))
    count = decode_1d(cursor.fetchone())
    cursor.close()
    if count[0] >= seat[0]:
        message1 = "The ticket of this flight is sold out. Please choose from other flights."
        session.pop('airline_name')
        session.pop('flight_num')
        return render_template("purchase.html", usertype = usertype, message1 = message1)

    else:
        message1 = "Confirm your purchase information."
        return render_template("purchase_confirm.html", usertype = usertype)

@app.route('/confirm', methods = ["GET", "POST"])
def confirm():
    if "usertype" not in session:
        return redirect("/")
    if "airline_name" not in session:
        return redirect("/")
    if "flight_num" not in session:
        return redirect("/")
    username = session["username"]
    usertype = session["usertype"]
    airline_name = session["airline_name"]
    flight_num = session["flight_num"]
    ticket_id = random.randint(10000, 99999)
    message = "Successfully Purchased!"

    if session["usertype"] == "staff":
        return redirect("/")


    cursor = conn.cursor(prepared=True)
    iticket = "Insert into ticket values(%s,%s,%s)"
    cursor.execute(iticket,(ticket_id, airline_name, flight_num))
    conn.commit()

    if usertype == "customer":
        # executes query
        query = "SELECT * FROM customer WHERE name =%s"
        cursor.execute(query,(username,))
        # stores the results in a variable
        data = decode_1d(cursor.fetchone())
        username = data[0]
        ipurchase = "Insert into purchases (ticket_id, customer_email,purchase_date) values(%s,%s,%s)"
        cursor.execute(ipurchase,(ticket_id, username,datetime.datetime.today().strftime('%Y-%m-%d')))
        conn.commit()

    else:
        # Find booking agent id
        query = "select booking_agent_id from booking_agent where email =%s"
        cursor.execute(query,(username,))
        booking_agent_id = decode_1d(cursor.fetchone())
        # insert to purchases
        customer_email = request.form["customer_email"]
        ipurchase = "Insert into purchases (ticket_id, customer_email, booking_agent_id,purchase_date) values(%s,%s,%s,%s)"
        cursor.execute(ipurchase,(ticket_id, customer_email, booking_agent_id[0],datetime.datetime.today().strftime('%Y-%m-%d')))
        conn.commit()

    cursor.close()


    session.pop('airline_name')
    session.pop('flight_num')

    return render_template("purchase.html", message = message, usertype = usertype)

@app.route('/view_commission', methods = ["GET", "POST"])
def view_commission():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "booking agent":
        return redirect("/")
    username = session["username"]
    select = request.form["select"]

    cursor = conn.cursor(prepared=True)

    book_id = "SELECT booking_agent_id FROM booking_agent WHERE email =%s"
    cursor.execute(book_id,(username,))
    booking_agent_id = decode_1d(cursor.fetchone())[0]

    if select == "no":
        tot = "SELECT SUM(price * 0.1) FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE booking_agent_id =%s\
            and DateDiff(CURDATE(), purchases.purchase_date) <= 30"
        cursor.execute(tot,(booking_agent_id,))
        tot_com = decode_1d(cursor.fetchone())[0]

        ave = "SELECT SUM(price * 0.1) / COUNT(ticket_id) FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE booking_agent_id =%s \
            and DateDiff(CURDATE(), purchases.purchase_date) <= 30"
        cursor.execute(ave,(booking_agent_id,))
        ave_com = decode_1d(cursor.fetchone())[0]
        sold = "SELECT COUNT(ticket_id) FROM ticket NATURAL JOIN purchases WHERE booking_agent_id =%s \
            and DateDiff(CURDATE(), purchases.purchase_date) <= 30"
        cursor.execute(sold,(booking_agent_id,))
        tot_sold = decode_1d(cursor.fetchone())[0]

    elif select == "yes":
        start = request.form["start"]
        end = request.form["end"]
        tot = "SELECT SUM(price * 0.1) FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE booking_agent_id =%s\
            and purchases.purchase_date between%s and%s"
        cursor.execute(tot,(booking_agent_id, start, end))
        tot_com = decode_1d(cursor.fetchone())[0]
        ave = "SELECT SUM(price * 0.1) / COUNT(ticket_id) FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE booking_agent_id =%s \
            and purchases.purchase_date between%s and%s"
        cursor.execute(ave,(booking_agent_id, start, end))
        ave_com = decode_1d(cursor.fetchone())[0]
        sold = "SELECT COUNT(ticket_id) FROM ticket NATURAL JOIN purchases WHERE booking_agent_id =%s \
            and purchases.purchase_date between%s and%s"
        cursor.execute(sold,(booking_agent_id, start, end))
        tot_sold = decode_1d(cursor.fetchone())[0]
    if tot_com == None:
        tot_com = 0
    if ave_com == None:
        ave_com = 0
    if tot_sold == None:
        tot_sold = 0

    return render_template("booking_agent_page.html", total_commission = round(tot_com,2),average_commission = round(ave_com,2), total_ticket = round(tot_sold,2), username=username)

@app.route('/customers_b')
def customers_b():
    if "usertype" not in session:
        return redirect("/")
    if session["usertype"] != "booking agent":
        return redirect("/")
    usertype = session["usertype"]

    cursor = conn.cursor(prepared=True)

    username = session["username"]
    t1 = "SELECT customer_email, name, COUNT(*) FROM purchases NATURAL JOIN booking_agent JOIN customer ON customer_email\
            = customer.email WHERE booking_agent.email =%s and DateDiff(CURDATE(), purchase_date)<365/2 \
                GROUP BY customer.email ORDER BY count(*) DESC LIMIT 5"
    t2 = "SELECT customer_email, name, SUM(price * 0.1)/COUNT(ticket_id) FROM purchases NATURAL JOIN booking_agent NATURAL JOIN ticket NATURAL JOIN flight JOIN customer ON customer_email \
         = customer.email WHERE booking_agent.email =%s and DateDiff(CURDATE(), purchase_date) < 365\
              GROUP BY customer.email ORDER BY SUM(price * 0.1)/COUNT(ticket_id) DESC LIMIT 5"
    cursor.execute(t1,(username,))
    customer = decode_2d(cursor.fetchall())
    conn.commit()
    cursor.execute(t2,(username,))
    customer_year = decode_2d(cursor.fetchall())
    conn.commit()
    email = []
    name = []
    ticket = []
    email_y = []
    name_y = []
    comms_y = []
    for i in customer:
        email.append(i[0])
        name.append(i[1])
        ticket.append(i[2])
    for i in customer_year:
        email_y.append(i[0])
        name_y.append(i[1])
        comms_y.append(i[2])
    if len(ticket) >0:
        maxi1 = max(ticket)
        maxi2 = max(comms_y)
    else:
        maxi1 = 100
        maxi2 = 100
    cursor.close()
    return render_template('customer.html', customer = customer, customer_y = customer_year, usertype = usertype,email = email, namee = name, ticket=ticket, email_y = email_y, name_y = name_y,comms_y=comms_y, maxi1 = maxi1, maxi2 = maxi2)

@app.route("/public_info")
def public_info():
    if "usertype" not in session:
        return redirect("/")
    scity = request.args.get('scity')
    dcity = request.args.get('dcity')
    date_search = request.args.get('date_search')
    flight_num = request.args.get('flight_num')
    dateof = request.args.get('dateof')
    date_check = request.args.get('date_check')
    flights = None
    statuses = None
    cursor = conn.cursor(prepared=True)
    if scity:
        query = """select * from flight, airport a1, airport a2
                where departure_airport = a1.airport_name and a1.airport_city = %s
                and arrival_airport = a2.airport_name and a2.airport_city = %s
                and departure_time LIKE %s and status = 'upcoming'"""
        cursor.execute(query,(scity, dcity, date_search+'%'))
        flights = decode_2d(cursor.fetchall())
    if flight_num:
        query = """select status from flight
                where flight_num = %s and {}_time LIKE %s""".format(dateof)
        cursor.execute(query,(flight_num, date_check+'%'))
        statuses = decode_2d(cursor.fetchall())
    cursor.close()
    return render_template('public_info.html', flights=flights, statuses=statuses)


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)

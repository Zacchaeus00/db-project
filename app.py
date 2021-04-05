from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
import json
app = Flask(__name__)
db = mysql.connector.connect(host='localhost',user = 'root',password = '123456',database = 'db_project')


@app.route("/")
def index():
	scity = request.args.get('scity')
	dcity = request.args.get('dcity')
	dept_date = request.args.get('dept_date')
	if not scity:
		return render_template('index.html', flights=None)
	cursor = db.cursor()
	query = """select * from flight, airport a1, airport a2 
			where departure_airport = a1.airport_name and a1.airport_city = '{}'
			and arrival_airport = a2.airport_name and a2.airport_city = '{}'
			and departure_time LIKE '{}%' and status = 'upcoming'"""
	cursor.execute(query.format(scity, dcity, dept_date))
	flights = cursor.fetchall()
	cursor.close()
	return render_template('index.html', flights=flights)
	
@app.route("/login")
def login():
	pass
	
@app.route("/signup")
def signup():
	pass
	

from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
import json
app = Flask(__name__)
dbconfig = json.load(open("dbconfig.json"))
db = mysql.connector.connect(host=dbconfig['host'],user=dbconfig['user'],password=dbconfig['password'],database=dbconfig['database'])


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
	return "to be implemented"
	
@app.route("/signup")
def signup():
	return "to be implemented"
	

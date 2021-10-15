from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import widgets, StringField, SubmitField, IntegerField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
app.config['SECRET_KEY'] = "hello"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#db_appie = 'test_database.db'

#conn = sqlite3.connect('annie.db', check_same_thread=False)
#cursor = conn.cursor()

################################################################################################

class NamerForm(FlaskForm):
	pseudonym = StringField(validators=[DataRequired()])
	submit = SubmitField("Enter")


################################################################################################

@app.route('/',  methods=['GET', 'POST'])
def index():
	global pseudonym
	pseudonym = None
	form = NamerForm()
	if form.validate_on_submit():
		pseudonym = form.pseudonym.data
		form.pseudonym.data = ''
		global conn
		global cursor
		conn = sqlite3.connect(pseudonym+'test.db', check_same_thread=False)
		cursor = conn.cursor()
	return render_template('index.html', pseudonym=pseudonym, form=form)

#@app.route('/make_database', methods=['GET', 'POST'])
#def make_database():
#	pseudonym = None
#	form = NamerForm()

#	return render_template('/make_database', pseudonym=pseudonym)

@app.route('/base')
def base():
	return render_template('base.html')

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/end_page')
def end_page():
	return render_template('end_page.html')


################################################################################################

@app.route('/make_table', methods=['GET', 'POST'])
def make_table():
	if request.method == 'POST':
		if request.form.get('Start') == 'Start':
			print(request.form.get('Start'))
			cursor = conn.cursor()
			cursor.execute("""DROP table IF EXISTS matches""")
			cursor.execute("""CREATE TABLE IF NOT EXISTS matches (
				feature text,
				ulsterscots integer, 
				derry integer,
				dublin integer,
				ruralsw integer
				)""")
	conn.commit()
	return render_template('goat_mouth.html')

@app.route('/matches', methods=['GET', 'POST'])
def matches():
   matches_data = query_matches_data()
   return render_template('matches.html', matches_data=matches_data)
   return matches_data


def query_matches_data():
	cursor = conn.cursor()
	cursor.execute("""
   SELECT * FROM matches
   """)
	matches_data = cursor.fetchall()
	return matches_data

##############################################################################################

@app.route('/see_results', methods=['GET', 'POST'])
def see_results():
	results_data = query_results()
	return render_template('see_results.html', results_data=results_data)
	return results_data

def query_results():
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM final ORDER BY percentage DESC")

	results_data = cursor.fetchall()
	return results_data


@app.route('/clear_table', methods=['GET', 'POST'])
def clear_table():
	cursor = conn.cursor()
	cursor.execute("""
	DROP table IF EXISTS matches
	""")
	conn.commit()
	cursor.execute("""
	DROP table IF EXISTS totals
	""")
	conn.commit()
	cursor.execute("""
	DROP table IF EXISTS totals2
	""")
	conn.commit()
	cursor.execute("""
	DROP table IF EXISTS totals3
	""")
	conn.commit()
	return render_template('matches.html')


@app.route('/make_results_table', methods=['GET', 'POST'])
def make_results_table():
	if request.method == 'POST':
		if request.form.get('Generate results') == 'Generate results':        	
			cursor = conn.cursor()
			cursor.execute("""DROP table IF EXISTS totals""")
			conn.commit()

			cursor.execute("""CREATE TABLE totals(
				feature real,
				ulsterscots real, 
				derry real,
				dublin real,
				ruralsw real
				)""")
			conn.commit()
			cursor.execute("INSERT INTO totals (feature, ulsterscots, derry, dublin, ruralsw) SELECT COUNT(feature), SUM(ulsterscots), SUM(derry), SUM(dublin), SUM(ruralsw) FROM matches;")
			conn.commit()


			cursor.execute("""DROP table IF EXISTS total2""")
			conn.commit()

			cursor.execute("""CREATE TABLE total2 (
				feature real,
				ulsterscots real, 
				derry real,
				dublin real,
				ruralsw real
				)""")
			conn.commit()
			cursor.execute("INSERT INTO total2 (feature, ulsterscots, derry, dublin, ruralsw) SELECT feature, (ulsterscots/feature)*100, (derry/feature)*100, (dublin/feature)*100, (ruralsw/feature)*100 FROM totals;")
			conn.commit()

			cursor.execute("""DROP table IF EXISTS usc""")
			conn.commit()

			#cursor.execute("""CREATE TABLE usc (
			#variety text,
			#percentage integer 
			#)""")
			#conn.commit()
			#cursor.execute("INSERT INTO usc VALUES ('Ulster Scots: ','')")
			#conn.commit()
			#cursor.execute("UPDATE usc (percentage) SELECT ulsterscots FROM total2;")
			#conn.commit()

			cursor.execute("""CREATE TABLE usc (
			variety text,
			percentage integer 
			)""")
			conn.commit()
			cursor.execute("INSERT INTO usc (percentage) SELECT ulsterscots FROM total2;")
			conn.commit()
			cursor.execute("UPDATE usc SET variety = 'Ulster Scots: '")
			conn.commit()


			cursor.execute("""DROP table IF EXISTS der""")
			conn.commit()

			cursor.execute("""CREATE TABLE der (
			variety text,
			percentage integer 
			)""")
			conn.commit()
			cursor.execute("INSERT INTO der (percentage) SELECT derry FROM total2;")
			cursor.execute("UPDATE der SET variety = 'Derry: '")
			conn.commit()

			cursor.execute("""DROP table IF EXISTS dublin""")
			conn.commit()

			cursor.execute("""CREATE TABLE dublin (
			variety text,
			percentage integer 
			)""")
			conn.commit()
			cursor.execute("INSERT INTO dublin (percentage) SELECT dublin FROM total2;")
			cursor.execute("UPDATE dublin SET variety = 'Dublin: '")
			conn.commit()

			cursor.execute("""DROP table IF EXISTS ruralsw""")
			conn.commit()

			cursor.execute("""CREATE TABLE ruralsw (
			variety text,
			percentage integer 
			)""")
			conn.commit()
			cursor.execute("INSERT INTO ruralsw (percentage) SELECT ruralsw FROM total2;")
			cursor.execute("UPDATE ruralsw SET variety = 'Kerry: '")
			conn.commit()

			cursor.execute("""DROP table IF EXISTS final""")
			conn.commit()

			cursor.execute("""CREATE TABLE final (
			variety text,
			percentage integer 
			)""")
			cursor.execute("INSERT INTO final (variety, percentage) SELECT variety, percentage FROM usc UNION SELECT variety, percentage FROM der UNION SELECT variety, percentage FROM dublin UNION SELECT variety, percentage FROM ruralsw;")
			conn.commit()

			cursor.execute("SELECT * FROM final ORDER BY percentage DESC")

			results_data = cursor.fetchall()
		conn.commit()
		return render_template('make_results_table.html', results_data=results_data)
		return results_data



################################################################################################---GOAT-MOUTH-

@app.route('/goat_mouth', methods=['GET', 'POST'])
def goat_mouth():
	return render_template('goat_mouth.html')

@app.route('/goat_mouth_save', methods=['GET', 'POST'])
def goat_mouth_save():
	if request.method == 'POST':
		if request.form.get('goat5') == '1':
			pass
		else:
			cursor = conn.cursor()
			cursor.execute("""INSERT INTO matches VALUES ('GOAT', '0', '0', '0', '0')""")
			if request.form.get('goat1') == '1':
				cursor.execute("""UPDATE matches SET ulsterscots = '1', derry = '1', ruralsw = '1' WHERE feature = 'GOAT'""")

			if request.form.get('goat2') == '1':
				cursor.execute("""UPDATE matches SET ulsterscots = '1' WHERE feature = 'GOAT'""")

			if request.form.get('goat3') == '1':
				cursor.execute("""UPDATE matches SET dublin = '1' WHERE feature = 'GOAT'""")

			if request.form.get('goat4') == '1':
				pass
			conn.commit()
		if request.form.get('mouth6') == '1':
			pass
		else:
			cursor = conn.cursor()
			cursor.execute("""INSERT INTO matches VALUES ('MOUTH', '0', '0', '0', '0')""")
			if request.form.get('mouth1') == '1':
				cursor.execute("""UPDATE matches SET ulsterscots = '1' WHERE feature = 'MOUTH'""")

			if request.form.get('mouth2') == '1':
				cursor.execute("""UPDATE matches SET derry = '1' WHERE feature = 'MOUTH'""")

			if request.form.get('mouth3') == '1':
				cursor.execute("""UPDATE matches SET dublin = '1' WHERE feature = 'MOUTH'""")

			if request.form.get('mouth4') == '1':
				cursor.execute("""UPDATE matches SET ruralsw = '1' WHERE feature = 'MOUTH'""")

			if request.form.get('mouth5') == '1':
				pass
			conn.commit()
	return render_template('fleece_near.html')


################################################################################################---FLEECE-NEAR-


@app.route('/fleece_near', methods=['GET', 'POST'])
def fleece_near():
	return render_template('fleece_near.html')

@app.route('/fleece_near_save', methods=['GET', 'POST'])
def fleece_near_save():
	if request.method == 'POST':
		if request.form.get('fleece3') == '1':
			pass
		if request.form.get('fleece2') == '1':
			pass
		if request.form.get('fleece1') == '1':
			cursor = conn.cursor()
			cursor.execute("""INSERT INTO matches VALUES ('FLEECE', '0', '0', '0', '0')""")
			cursor.execute("""UPDATE matches SET dublin = '1' WHERE feature = 'FLEECE'""")
			conn.commit()
		
		if request.form.get('near4') == '1':
			pass
		else:
			cursor = conn.cursor()
			cursor.execute("""INSERT INTO matches VALUES ('NEAR', '0', '0', '0', '0')""")
			if request.form.get('near1') == '1':
				cursor.execute("""UPDATE matches SET derry = '1' WHERE feature = 'NEAR'""")

			if request.form.get('near2') == '1':
				cursor.execute("""UPDATE matches SET dublin = '1' WHERE feature = 'NEAR'""")

			if request.form.get('near3') == '1':
				cursor.execute("""UPDATE matches SET ulsterscots = '1', derry = '1', dublin = '1', ruralsw = '1' WHERE feature = 'NEAR'""")
			conn.commit()
	return render_template('end_page.html')

@app.route('/happy_kit', methods=['GET', 'POST'])
def happy_kit():
	return render_template('happy_kit.html')

@app.route('/save_happy_kit', methods=['GET', 'POST'])
def save_happy_kit():
	return render_template('end_page.html')

################################################################################################

if __name__ == '__main__':
	app.run(debug=True)
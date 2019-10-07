
import os
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import stripe
import pandas as pd 

app = Flask(__name__)

bootstrap = Bootstrap(app)
##################

symbol = ""
start = ""
end = ""
data = pd.DataFrame()
comp_name = ""

#Stripe
publish_key = 'SR'
secret_key = 'SR'

stripe_keys = {
  'secret_key': 'SR',
  'publishable_key': 'SR'
}

stripe.api_key = stripe_keys['secret_key']
########################

# 
# export SECRET_KEY=mysecret  Linux
# set SECRET_KEY=mysecret  Windows
app.config['SECRET_KEY'] = 'secretkey'


############################
### DATABASE SETUP ##########
########################

#set FLASK_APP=app.py
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

#########################


################################################### User Managemet #######################################
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

##########################################################################################################33

##################################### Main App config #######################################################
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))

		return '<h1>Invalid username or password</h1>'
		#return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

	return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()

	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()

		return  redirect(url_for('payment'))
		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

	return render_template('signup.html', form=form)

@app.route('/payment')
def payment():
    return render_template('payment.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    try:
        amount = 100   # amount in cents
        customer = stripe.Customer.create(
            email='sample@customer.com',
            source=request.form['stripeToken']
        )
        stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='USD',
            description='Prediction Charge'
        )
        return render_template('dashboard.html', amount=amount)
    except stripe.error.StripeError:
        return render_template('error.html')

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

#####################################################################################################3



######################################################################################
#####                  Machine Learning Section                       ###############
######################################################################################

import pandas_datareader.data as web
from prophet import *
@app.route('/predict',methods=["POST", 'GET'])
@login_required
def predict():

	#global symbol
	#global start
	#global end
	#global data
	#global comp_name

	if request.method=='POST':
		print(request)
		# if symbol != request.form['search']:
		symbol = request.form['symbol']
		start = request.form['date-start']
		end = request.form['date-end']
		data = load_ticker(symbol, start, end)
		plot_price = analysis(data)
		plot_model = PlotPhModel(data)
		plot_comp = PlotPhComp(data)
		
		#data = datatoget.load_ticker(symbol,start, end) 
		#return render_template("predict.html", df = company.load_ticker(symbol, start, end))
		#return render_template("dashboard.html")
		return render_template("predict.html", symbol=symbol, start=start, end = end, plot_price=plot_price, plot_model=plot_model, plot_comp=plot_comp)

def load_ticker(ticker, start, end):
	"""An almost-pointlessly short utility function to scrape ticker data,
	and put it in a pandas df. Will have more features added in future.
	"""
	df = web.DataReader(ticker, 'yahoo', start, end)
	#df.reset_index(inplace=True,drop=False)
#	df.to_csv(df)
	##save the data for further used
	#filename= "./doc/"+ticker+ "_stock_data.csv"
	#print(filename)
	#df.to_csv(filename)
	return df
#############################################################




#################################################################
##############################   Strip payment   ##########################















if __name__ == '__main__':
	app.run()

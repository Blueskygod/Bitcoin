from flask import Flask, render_template, url_for, redirect, session, flash, send_file, json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, file_allowed
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import uuid as uuid
from datetime import timedelta
import os
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"Placeholder": "Usename"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"Placeholder": "Password"})
    submit = SubmitField("Register")

def validate_username(self, username):
    existing_user_username = User.query.filter_by(
        username=username.data).first()
    if existing_user_username:
        raise ValidationError(
            "That username is already exists. Please choose the different one"
        )

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"Placeholder": "Usename"})
    password= PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"Placeholder": "Password"})
    submit = SubmitField("Login")

@app.route('/')
def home():
    URL = "https://www.coindesk.com/price/bitcoin/"
    response = requests.get(URL)
    htmlContent = bs(response.content, 'html.parser')
    divTagContent = htmlContent.find('div', {'class':'dmKGkL'})
    price = divTagContent.select('span')
    return render_template('home.html',price=price[1].text) #price=price

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('user'))
    return render_template('login.html', form=form)

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    return render_template('user.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user=User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/shop', methods=['GET', 'POST'])
@login_required
def shop():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data #First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) #then save the file
        return "File has been uploaded."
    return render_template('shop.html', form=form)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)


#Json Thing
#@app.route('/date')
#def get_date():
# favorite_pizza={
#     "John": "Pepperoni",
#     "Mary": "Cheese",
#     "Tim": "Mushroom"
# }
# return favorite_pizza 

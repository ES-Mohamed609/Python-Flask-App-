import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, redirect, url_for, request, flash, session
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from db import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

from models import User, Contact
from forms import LoginForm, RegistrationForm, ContactForm
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yourpassword@localhost/ContactApp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            return redirect(url_for('contact_list'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/contact_list')
def contact_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    contacts = Contact.query.filter_by(user_id=user.id).all()
    return render_template('contact_list.html', contacts=contacts)

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    form = ContactForm()
    if form.validate_on_submit():
        new_contact = Contact(
            user_id=session['user_id'],
            full_name=form.full_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data
        )
        db.session.add(new_contact)
        db.session.commit()
        flash('Contact has been added!', 'success')
        return redirect(url_for('contact_list'))
    return render_template('add_contact.html', form=form)

@app.route('/contact/<int:contact_id>', methods=['GET', 'POST'])
def contact_details(contact_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    contact = Contact.query.get_or_404(contact_id)
    if contact.user_id != session['user_id']:
        return redirect(url_for('contact_list'))

    form = ContactForm(obj=contact)
    if form.validate_on_submit():
        contact.full_name = form.full_name.data
        contact.email = form.email.data
        contact.phone_number = form.phone_number.data
        db.session.commit()
        flash('Contact updated successfully!', 'success')
        return redirect(url_for('contact_list'))
    return render_template('contact_details.html', form=form)

@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    contact = Contact.query.get_or_404(contact_id)
    if contact.user_id != session['user_id']:
        return redirect(url_for('contact_list'))

    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('contact_list'))

if __name__ == '__main__':
    app.run(debug=True)
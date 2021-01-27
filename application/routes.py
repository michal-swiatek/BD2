from flask import render_template, flash, redirect, url_for

from application import app
from application.forms import RegistrationForm, LoginForm

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", title="Login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f"Successfully logged in!", "success")
        return redirect(url_for('home'))

    return render_template("login.html", title="Login", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.login.data}! Password set to: {'abcd'}", "success")
        return redirect(url_for('home'))

    return render_template("register.html", title="Register", form=form)

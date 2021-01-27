from flask import render_template, flash, redirect, url_for

from application import app
from application.forms import RegistrationForm, LoginForm
from application.database import validate_user, create_account, logout as db_logout

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", title="Login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and validate_user(form.login, form.password):
        flash(f"Successfully logged in!", "success")
        return redirect(url_for('home'))

    return render_template("login.html", title="Login", form=form)

@app.route('/logout')
def logout():
    db_logout()
    flash(f"Successfully logged out!", "success")
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = create_account(form.name.data, form.surname.data, form.login.data, form.email.data, form.role.data)
        if password is not None:
            flash(f"Account created for {form.login.data}! Password set to: {password}", "success")
        else:
            flash(f"Only admins can create accounts!", "info")
        return redirect(url_for('home'))

    return render_template("register.html", title="Register", form=form)

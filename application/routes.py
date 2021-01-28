from flask import render_template, flash, redirect, url_for

from application import app
from application.forms import RegistrationForm, LoginForm
from application.accounts import validate_user, create_account, db_login, db_logout
from application.browse_offer import get_catering_data

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", title="Login")

@app.route('/catering')
def catering():
    catering_data = get_catering_data()

    return render_template("catering.html", title="Catering", catering_data=catering_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and validate_user(form.login, form.password):
        db_login(form.login)
        flash(f"Successfully logged in as {form.login.data}!", "success")
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
        password = create_account(form.name.data, form.surname.data, form.login.data, form.email.data, form.role.data, form.department.data)
        if password is not None:
            flash(f"Account created for {form.login.data}! Password set to: {password}", "success")
        else:
            flash(f"Only admins can create accounts!", "info")

        # delete_account()

        return redirect(url_for('home'))

    return render_template("register.html", title="Register", form=form)

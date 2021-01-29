import json
import asyncio
import time

from flask import render_template, flash, redirect, url_for, request, session

from application import app
from application.forms import RegistrationForm, LoginForm, UpdateForm, DeleteForm
from application.accounts import validate_user, create_account, db_login, db_logout, modify_password, delete_account
from application.reservations import get_reservations
from application.browse_offer import get_catering_data, get_reservation_data, get_projects, get_offer, get_role

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():

    if 'username' in session.keys():
        msg = session['username']
    else:
        msg = None
    return render_template("home.html", username=msg, title="Login")



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and validate_user(form.login, form.password):

        db_login(form.login)

        session['username'] = form.login.data
        current_role = get_role(session['username'])
        session['role'] = current_role

        flash(f"Successfully logged in as {session['username']}", "success")
        # flash(f"Successfully logged in as {form.login.data}!", "success")
        return redirect(url_for('home'))

    return render_template("login.html", title="Login", form=form)



@app.route('/logout')
def logout():
    db_logout()
    try:
        session.pop("username")
        session.pop("role")
    except:
        pass
    flash(f"Successfully logged out!", "success")
    return redirect(url_for('home'))



@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():
        if session['role'] == "admin":
            password = create_account(form.name.data, form.surname.data, form.login.data, form.email.data, form.role.data, form.department.data)
            if password is not None:
                flash(f"Account created for {form.login.data}! Password set to: {password}", "success")
        else:
            flash(f"Only admins can create accounts!", "warning")

        return redirect(url_for('home'))

    return render_template("register.html", title="Register", form=form)


@app.route('/update_account', methods=['GET', 'POST'])
def update_account():

    form = UpdateForm()
    if 'username' not in session.keys():
        # message to user here later
        return redirect(url_for('login'))

    if form.validate_on_submit():
        if (session['username'] == form.username.data or session['role'] == 'admin'):

            if form.new_password.data == form.confirm_new_password.data:
                # ALLOW_modification
                modify_password(form.username.data, form.new_password.data)
                flash(f"Successfully modified personal data", "success")
            else:
                flash(f"Passwords don't match")
        else:
            flash(f"You're allowed to modify only your account", "warning")

        return redirect(url_for('home'))

    return render_template("update_account.html", form=form)

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():

    form = DeleteForm()
    if 'username' not in session.keys():
        # message to user here later
        return redirect("login.html")

    if form.validate_on_submit():
        if session['username'] == form.username.data or session['role'] == 'admin':

            delete_account(form.username.data)

            try:
                session.pop("username")
                session.pop("role")
            except:
                pass
            flash(f"Successfully logged out!", "success")

            return redirect(url_for("home"))
        else:
            flash(f"Can't delete an account", "warning")

    return render_template("delete_account.html", form=form)


@app.route('/catering', methods=["GET", "POST"])
def catering():
    catering_data = get_catering_data()

    if request.method == "POST":
        print("Inside catering")
        print(request.json)

    return render_template("catering.html", title="Catering", catering_data=catering_data)



@app.route('/offers/<int:catering_id>', methods=["GET", "POST"])
def offer(catering_id):

    print(catering_id)

    offers = get_offer(catering_id)
    print(offers)
    print(session["room_id"])

    print('itsme')

    if request.method == "POST":
        print(request.json)
        # TODO: better parse json here
        session["products"] = request.json

    return render_template("offers.html",
                           title="Offers",
                           headings=["Product name", "Price", "Max order", "Description"],
                           products_data=offers)




@app.route('/reservations', methods=["GET", "POST"])
def reservations():

    headings = ["city", "building", "street", "number", "zipcode", "Room Number", "Available seats", "Area", "Room id"]
    reservation_data = get_reservation_data()


    if request.method == "POST":

        session["room_id"] = request.json
        print(session["room_id"])
    #
    #     room_id = request.form.get("room_id")
    #     print(room_id)


    # def print_id(room_id):
    #     print(room_id)

    return render_template("reservations.html",
                           title="Reservations",
                           headings=headings,
                           reservation_data=reservation_data)




@app.route('/reservation_form')
def make_reservation():
    reservations = get_reservations('01.01.1999', '31.01.2021', 2)

    return render_template("make_reservation.html", title="Reservation", reservations=reservations)



@app.route('/projects')
def list_projects():

    projects_data = get_projects()

    return render_template("projects.html",
                           headings=["Project Title"],
                           title="Projects",
                           projects_data=projects_data)




@app.route('/reports')
def make_reports():

    current_role = get_role(session['username'])

    if current_role != 'manager':
        flash(f"You're logged as a {current_role}.Permission denied. Reports are available only for managers", "error")

        return redirect('/home')
    else:
        return render_template("reports.html", message=f"Welcome, {session['username']}")
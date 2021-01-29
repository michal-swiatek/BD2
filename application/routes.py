import json

from flask import render_template, flash, redirect, url_for, request

from application import app
from application.forms import RegistrationForm, LoginForm
from application.accounts import validate_user, create_account, db_login, db_logout
from application.reservations import get_reservations
from application.browse_offer import get_catering_data, get_reservation_data, get_projects


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", title="Login")

@app.route('/catering')
def catering():
    catering_data = get_catering_data()

    return render_template("catering.html", title="Catering", catering_data=catering_data)

@app.route('/reservation_form')
def make_reservation():
    reservations = get_reservations('01.01.1999', '31.01.2021', 2)

    return render_template("make_reservation.html", title="Catering", reservations=reservations)

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




@app.route('/reservations', methods=["GET", "POST"])
def reservations():

    headings = ["city", "building", "street", "number", "zipcode", "Room Number", "Available seats", "Area", "Room id"]
    reservation_data = get_reservation_data()



    if request.method == "POST":
        print(request.json)
    #
    #     room_id = request.form.get("room_id")
    #     print(room_id)


    # def print_id(room_id):
    #     print(room_id)

    return render_template("reservations.html",
                           title="Reservations",
                           headings=headings,
                           reservation_data=reservation_data,
                           make_reservation=make_reservation)


@app.route('/projects')
def list_projects():

    projects_data = get_projects()

    return render_template("projects.html",
                           headings=["Project Title"],
                           title="Projects",
                           projects_data=projects_data)

@app.route('/report')
def make_reports():
    pass
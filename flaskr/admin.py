#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
admin.py contains the control logic for all pages for user_type=Admin
"""
from flask import Blueprint, flash, g, redirect
from flask import render_template, request, url_for, session
from auth import login_required
from forms import AdminCarSearchForm, AdminUserSearchForm, RegisterForm, AdminUpdateUserForm, AdminCreateCarForm, AdminUpdateCarForm, NewBacklogForm
from model.car import Car
from model.account import Account
from model.booking import Booking
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from auth import login_required
import requests
import json
import smtplib

admin = Blueprint("admin", __name__)

@admin.route("/users", methods=("GET", "POST"))
@login_required
def user_view():
    """
    This is the user search function for Admin users. If you access it via GET request, we assume you are arriving for the first time and display a search form with no listed users. If you access it via POST request, we assume you've completed the search form and instead return both the search form and a table with results. Only Admin has access.
    """
    if (g.type != "Admin"):
        return "Access Denied"
    form = AdminUserSearchForm()
    if request.method == "POST":
        return search_user(form)
    if request.method == "GET":
        return display_all_users(form)

def search_user(form):
    """This is the control logic that receives data from WTForms and returns users."""
    username = request.form['username'].strip()
    firstname = request.form['firstname'].strip()
    lastname = request.form['lastname'].strip()
    phone = request.form['phone'].strip()
    email = request.form['email'].strip()
    user_type = request.form['user_type'].strip().lower()
    users = []
    if validate_search_input(username, phone, email):
        if user_type == "":
            users = requests.get("http://127.0.0.1:8080/customers/read?username={}&first_name={}&last_name={}&email={}&phone={}"
                .format(username, firstname, lastname, email, phone)).json()
            staffs = requests.get("http://127.0.0.1:8080/staffs/read?username={}&first_name={}&last_name={}&email={}&phone={}&user_type={}"
                .format(username, firstname, lastname, email, phone, user_type)).json()
            users.extend(staffs)
        elif user_type == "customer":
            users = requests.get("http://127.0.0.1:8080/customers/read?username={}&first_name={}&last_name={}&email={}&phone={}"
                .format(username, firstname, lastname, email, phone)).json()
        elif user_type == "admin" or user_type == "manager" or user_type == "engineer":
            users = requests.get("http://127.0.0.1:8080/staffs/read?username={}&first_name={}&last_name={}&email={}&phone={}&user_type={}"
                .format(username, firstname, lastname, email, phone, user_type)).json()
        # all in the search box will return all the tuples
        return render_template("admin/user_view.html", users=users, form=form)
    return display_all_users(form)

def validate_search_input(username, phone, email):
    """
    This is the validation logic for the user search form. We check username and phone number against a regex if they exist.
    """
    if username != "" and not Account.validate_username_input(username):
        return False
    if phone != "" and not Account.validate_phone_input(phone):
        return False
    return True

def display_all_users(form):
    """If no search fields are filled, we show all users with this function."""
    users = requests.get("http://127.0.0.1:8080/customers/read?").json()
    staffs = requests.get("http://127.0.0.1:8080/staffs/read?").json()
    users.extend(staffs)
    return render_template("admin/user_view.html", users=users, form=form)

@admin.route("/update/user", methods=("GET", "POST"))
@login_required
def update_user():
    """This page provides a form for the admin user to update users on GET. On POST, it updates the user instead. Parameters:
    
    user_id: The id of the user
    user_type: The type of the user, e.g. engineer
    """
    if (g.type != "Admin"):
        return "Access Denied"
    try:
        user_type = request.args["user_type"]
    except:
        user_type = "customers"
    form = AdminUpdateUserForm()
    try:
        user_type = request.args["user_type"]
    except:
        user_type = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        firstname = request.form["firstname"].strip()
        lastname = request.form["lastname"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        mac_address = request.form["mac_address"].strip()
        account = Account(username, password, email, firstname, lastname, phone, request.args["user_id"], mac_address)
        if account.validate_update_account():
            account.update_account(user_type)
            return redirect(url_for("admin.user_view"))
    return render_template("admin/update_user.html", user_id=request.args["user_id"], user_type=user_type, form=form)
        
@admin.route("/delete/user", methods=("GET", "POST"))
@login_required
def delete_user():
    """
    This lets the admin user delete users -- it is never called directly as a view but only by a button.
    """
    if (g.type != "Admin"):
        return "Access Denied"    
    if request.args["user_type"] == "":
        requests.put("http://127.0.0.1:8080/bookings/remove/customer?customer_id=" + request.args["user_id"])
        requests.delete("http://127.0.0.1:8080/customers/delete?id=" + request.args["user_id"])
    elif request.args["user_type"] == "Engineer":
        requests.put("http://127.0.0.1:8080/backlogs/remove/signed/engineer?id=" + request.args["user_id"])
        requests.put("http://127.0.0.1:8080/backlogs/remove/assigned/engineer?id=" + request.args["user_id"])
        requests.delete("http://127.0.0.1:8080/staffs/delete?id=" + request.args["user_id"])
    else:
        requests.delete("http://127.0.0.1:8080/staffs/delete?id=" + request.args["user_id"])
    flash("User deleted!")
    return redirect(url_for("admin.user_view"))

@admin.route("/cars", methods=("GET", "POST"))
@login_required
def car_view():
    """
    This is the car search function for Admin users. If you access it via GET request, we assume you are arriving for the first time and display a search form with no listed cars. If you access it via POST request, we assume you've completed the search form and instead return both the search form and a table with results. Only Admin has access.
    """
    if (g.type != "Admin"):
        return "Access Denied"
    form = AdminCarSearchForm()
    if request.method == "POST":
        return search_car(form)
    return display_all_cars(form)

def search_car(form):
    """This is the control logic that receives data from WTForms and returns cars."""
    brand = request.form['brand'].strip()
    car_type = request.form['car_type'].strip()
    color = request.form['color'].strip()
    seat = request.form['seat'].strip()
    cost = request.form['cost'].strip()
    mac_address = request.form['mac_address'].strip()
    if not Booking.validate_cost(cost):
        return display_all_cars(form)
    cars = requests.get(
        "http://127.0.0.1:8080/cars/read?brand={}&type={}&color={}&seat={}&cost={}&mac_address={}"
        .format(brand, car_type, color, seat, cost, mac_address)
    ).json()
    return render_template("admin/car_view.html", cars=cars, form=form)

def display_all_cars(form):
    """If no search fields are filled or under certain errors, we show all users with this function."""
    cars = requests.get(
        "http://127.0.0.1:8080/cars/read?"
    ).json()
    return render_template("admin/car_view.html", cars=cars, form=form)

@admin.route("/car/bookings", methods=("GET", "POST"))
@login_required
def car_bookings():
    """
    This gets all bookings for a given car. It's accessed by pressing a button on the admin car search page.
    """
    if (g.type != "Admin"):
        return "Access Denied"
    bookings = requests.get("http://127.0.0.1:8080/cars/history?id={}".format(request.args["car_id"])).json()
    return render_template("admin/car_bookings.html", bookings=bookings, id=request.args["car_id"])

@admin.route("/create/car", methods=("GET", "POST"))
@login_required
def create_car():
    """This loads a form for the admin user to create a new car"""
    if (g.type != "Admin"):
        return "Access Denied"
    form = AdminCreateCarForm()
    if request.method == "POST":
        mac_address = request.form["mac_address"].strip()
        brand = request.form["brand"].strip()
        car_type = request.form["car_type"].strip()
        color = request.form["color"].strip()
        seat = request.form["seat"].strip()
        location_id = request.form["location_id"].strip()
        cost = request.form["cost"].strip()
        car = Car(brand, car_type, color, seat, cost, location_id, mac_address)
        if car.validate_new_car():
            car.create_car()
            return redirect(url_for("admin.car_view"))
    return render_template("admin/car_detail.html", form=form)

@admin.route("/update/car", methods=("GET", "POST"))
@login_required
def update_car():
    """On POST request, this creates a car. On GET, it returns a form to fill out to update a car. Parameters:
    
    car_id: The id of the car to update.
    """
    if g.type != "Admin":
        return "Access Denied"
    form = AdminUpdateCarForm()
    if request.method == "POST":
        mac_address = request.form["mac_address"].strip()
        brand = request.form["brand"].strip()
        car_type = request.form["car_type"].strip()
        color = request.form["color"].strip()
        seat = request.form["seat"].strip()
        location_id = request.form["location_id"].strip()
        cost = request.form["cost"].strip()
        status = request.form["status"].strip()
        car = Car(brand, car_type, color, seat, cost, location_id, mac_address, status)
        if car.validate_update_car():
            car.update_car(request.args["car_id"])
            return redirect(url_for("admin.car_view"))
    return render_template("admin/car_detail.html", car_id=request.args["car_id"], form=form, action="update")

@admin.route("/delete/car", methods=("POST","GET"))
@login_required
def delete_car():
    """
    This deletes a car. Parameters:
    
    car_id: The id of the car to delete
    """
    if (g.type != "Admin"):
        return "Access Denied"
    requests.put("http://127.0.0.1:8080/backlogs/remove/car?car_id=" + request.args["car_id"])
    requests.put("http://127.0.0.1:8080/bookings/remove/car?car_id=" + request.args["car_id"])
    requests.delete("http://127.0.0.1:8080/cars/delete?id=" + request.args["car_id"])
    flash("Car deleted!")
    return redirect(url_for("admin.car_view"))

@admin.route("/report/car", methods=("POST","GET"))
@login_required
def report_car():
    """
    This flags a car to be repaired by an engineer. Accessed by searching for a car, then selecting the update button.
    """
    if (g.type != "Admin"):
        return "Access Denied"
    car = requests.get("http://127.0.0.1:8080/cars/read?id=" + str(request.args["car_id"])).json()[0]
    engineer = requests.get("http://127.0.0.1:8080/staffs/read?user_type=engineer").json()[0]
    form = NewBacklogForm()
    if request.method == "POST":
        description = request.form["description"].strip()
        requests.put(
            "http://127.0.0.1:8080/cars/update?status=To be repaired" +
            "&discription=" + description +
            "&id=" + str(request.args["car_id"])
        )
        send_email(engineer["Email"], str(request.args["car_id"]), description)
        requests.post("http://127.0.0.1:8080/backlogs/create?assigned_engineer_id={}&car_id={}&status=Not%20done&description={}"
                .format(str(engineer["ID"]), str(car["ID"]), str(description)))
        return redirect(url_for("admin.car_view"))
    return render_template("admin/confirm_report.html", form=form, car=car, engineer=engineer)
     
def send_email(receiver, car_id, description):
    """
    This sends out an email to an engineer when a new repair request is made. We used a HTML email template from [https://github.com/leemunroe/responsive-html-email-template] and modified it with the input to this function. Parameters:
    
    receiver: Email address of the person receiving the email. 
    car_id: The car_id that needs repair
    description: A short description of the repairs to make.
    
    Note that the sending address needs to have 'allow less secure' authentication methods enabled in Gmail so that it can use smtp authentication instead of OAuth2.
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = "Car Maintenance Request"
    message["From"] = "ahjhj24012000@gmail.com"
    message["To"] = receiver
    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    How are you?"""
    html = """\
    <!doctype html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Simple Transactional Email</title>
        <style>
        /* -------------------------------------
            GLOBAL RESETS
        ------------------------------------- */
        
        /*All the styling goes here*/
        
        img {
            border: none;
            -ms-interpolation-mode: bicubic;
            max-width: 100%; 
        }

        body {
            background-color: #f6f6f6;
            font-family: sans-serif;
            -webkit-font-smoothing: antialiased;
            font-size: 14px;
            line-height: 1.4;
            margin: 0;
            padding: 0;
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%; 
        }

        table {
            border-collapse: separate;
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
            width: 100%; }
            table td {
            font-family: sans-serif;
            font-size: 14px;
            vertical-align: top; 
        }

        /* -------------------------------------
            BODY & CONTAINER
        ------------------------------------- */

        .body {
            background-color: #f6f6f6;
            width: 100%; 
        }

        /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
        .container {
            display: block;
            margin: 0 auto !important;
            /* makes it centered */
            max-width: 580px;
            padding: 10px;
            width: 580px; 
        }

        /* This should also be a block element, so that it will fill 100% of the .container */
        .content {
            box-sizing: border-box;
            display: block;
            margin: 0 auto;
            max-width: 580px;
            padding: 10px; 
        }

        /* -------------------------------------
            HEADER, FOOTER, MAIN
        ------------------------------------- */
        .main {
            background: #ffffff;
            border-radius: 3px;
            width: 100%; 
        }

        .wrapper {
            box-sizing: border-box;
            padding: 20px; 
        }

        .content-block {
            padding-bottom: 10px;
            padding-top: 10px;
        }

        .footer {
            clear: both;
            margin-top: 10px;
            text-align: center;
            width: 100%; 
        }
            .footer td,
            .footer p,
            .footer span,
            .footer a {
            color: #999999;
            font-size: 12px;
            text-align: center; 
        }

        /* -------------------------------------
            TYPOGRAPHY
        ------------------------------------- */
        h1,
        h2,
        h3,
        h4 {
            color: #000000;
            font-family: sans-serif;
            font-weight: 400;
            line-height: 1.4;
            margin: 0;
            margin-bottom: 30px; 
        }

        h1 {
            font-size: 35px;
            font-weight: 300;
            text-align: center;
            text-transform: capitalize; 
        }

        p,
        ul,
        ol {
            font-family: sans-serif;
            font-size: 14px;
            font-weight: normal;
            margin: 0;
            margin-bottom: 15px; 
        }
            p li,
            ul li,
            ol li {
            list-style-position: inside;
            margin-left: 5px; 
        }

        a {
            color: #3498db;
            text-decoration: underline; 
        }

        /* -------------------------------------
            BUTTONS
        ------------------------------------- */
        .btn {
            box-sizing: border-box;
            width: 100%; }
            .btn > tbody > tr > td {
            padding-bottom: 15px; }
            .btn table {
            width: auto; 
        }
            .btn table td {
            background-color: #ffffff;
            border-radius: 5px;
            text-align: center; 
        }
            .btn a {
            background-color: #ffffff;
            border: solid 1px #3498db;
            border-radius: 5px;
            box-sizing: border-box;
            color: #3498db;
            cursor: pointer;
            display: inline-block;
            font-size: 14px;
            font-weight: bold;
            margin: 0;
            padding: 12px 25px;
            text-decoration: none;
            text-transform: capitalize; 
        }

        .btn-primary table td {
            background-color: #3498db; 
        }

        .btn-primary a {
            background-color: #3498db;
            border-color: #3498db;
            color: #ffffff; 
        }

        /* -------------------------------------
            OTHER STYLES THAT MIGHT BE USEFUL
        ------------------------------------- */
        .last {
            margin-bottom: 0; 
        }

        .first {
            margin-top: 0; 
        }

        .align-center {
            text-align: center; 
        }

        .align-right {
            text-align: right; 
        }

        .align-left {
            text-align: left; 
        }

        .clear {
            clear: both; 
        }

        .mt0 {
            margin-top: 0; 
        }

        .mb0 {
            margin-bottom: 0; 
        }

        .preheader {
            color: transparent;
            display: none;
            height: 0;
            max-height: 0;
            max-width: 0;
            opacity: 0;
            overflow: hidden;
            mso-hide: all;
            visibility: hidden;
            width: 0; 
        }

        .powered-by a {
            text-decoration: none; 
        }

        hr {
            border: 0;
            border-bottom: 1px solid #f6f6f6;
            margin: 20px 0; 
        }

        /* -------------------------------------
            RESPONSIVE AND MOBILE FRIENDLY STYLES
        ------------------------------------- */
        @media only screen and (max-width: 620px) {
            table[class=body] h1 {
            font-size: 28px !important;
            margin-bottom: 10px !important; 
            }
            table[class=body] p,
            table[class=body] ul,
            table[class=body] ol,
            table[class=body] td,
            table[class=body] span,
            table[class=body] a {
            font-size: 16px !important; 
            }
            table[class=body] .wrapper,
            table[class=body] .article {
            padding: 10px !important; 
            }
            table[class=body] .content {
            padding: 0 !important; 
            }
            table[class=body] .container {
            padding: 0 !important;
            width: 100% !important; 
            }
            table[class=body] .main {
            border-left-width: 0 !important;
            border-radius: 0 !important;
            border-right-width: 0 !important; 
            }
            table[class=body] .btn table {
            width: 100% !important; 
            }
            table[class=body] .btn a {
            width: 100% !important; 
            }
            table[class=body] .img-responsive {
            height: auto !important;
            max-width: 100% !important;
            width: auto !important; 
            }
        }

        /* -------------------------------------
            PRESERVE THESE STYLES IN THE HEAD
        ------------------------------------- */
        @media all {
            .ExternalClass {
            width: 100%; 
            }
            .ExternalClass,
            .ExternalClass p,
            .ExternalClass span,
            .ExternalClass font,
            .ExternalClass td,
            .ExternalClass div {
            line-height: 100%; 
            }
            .apple-link a {
            color: inherit !important;
            font-family: inherit !important;
            font-size: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
            text-decoration: none !important; 
            }
            #MessageViewBody a {
            color: inherit;
            text-decoration: none;
            font-size: inherit;
            font-family: inherit;
            font-weight: inherit;
            line-height: inherit;
            }
            .btn-primary table td:hover {
            background-color: #34495e !important; 
            }
            .btn-primary a:hover {
            background-color: #34495e !important;
            border-color: #34495e !important; 
            } 
        }

        </style>
    </head>
    <body class="">
        <span class="preheader">This is preheader text. Some clients will show this text as a preview.</span>
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
        <tr>
            <td>&nbsp;</td>
            <td class="container">
            <div class="content">

                <!-- START CENTERED WHITE CONTAINER -->
                <table role="presentation" class="main">

                <!-- START MAIN CONTENT AREA -->
                <tr>
                    <td class="wrapper">
                    <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                        <tr>
                        <td>
                            <p>Hello engineer,</p>
                            <p>Repairs have been requested for car #""" + car_id + " #"+ description + """</p>
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="btn btn-primary">
                            <tbody>
                                <tr>
                                <td align="left">
                                    <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                    <tbody>
                                        <tr>
                                        <td> <a href=\"""" + "http://127.0.0.1:5000/auth/login" + """\" target="_blank">Click here to login</a> </td>
                                        </tr>
                                    </tbody>
                                    </table>
                                </td>
                                </tr>
                            </tbody>
                            </table>
                            <p>Once logged in, you can see the car's location. Remember to mark the car as repaired when finished!</p>
                            <p>Have a great day.</p>
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>

                <!-- END MAIN CONTENT AREA -->
                </table>
                <!-- END CENTERED WHITE CONTAINER -->

                <!-- START FOOTER -->
                <div class="footer">
                <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                    <tr>
                    <td class="content-block">
                        <span class="apple-link">CloudCar, 123 Fake Street, HCMC Vietnam 700000</span>
                        
                    </td>
                    </tr>
                    <tr>
                    <td class="content-block powered-by">
                        Powered by <a href="https://github.com/leemunroe/responsive-html-email-template">HTMLemail</a>.
                    </td>
                    </tr>
                </table>
                </div>
                <!-- END FOOTER -->

                </div>
                </td>
                <td>&nbsp;</td>
            </tr>
            </table>
        </body>
    </html>
    """
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("ahjhj24012000@gmail.com", "quoc2401@")
    server.sendmail("ahjhj24012000@gmail.com", "quoccuong242000@gmail.com", message.as_string())

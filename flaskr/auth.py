#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auth.py contains all the functions related to user authentication.
"""
from flask import Blueprint, flash, g, redirect
from flask import render_template, request, session, url_for
from model.account import Account
from forms import LoginForm, RegisterForm
import functools
import requests

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=("GET", "POST"))
def login():
    """
    This is the login form. The form code is located in forms.py. If you pass it a GET request, it serves you the form. If you pass it a POST request, it treats it as a form submission. Parameters:
    
    username: your username
    password: your password
    
    On submission, if your credentials are correct, it will create a session for the logged in user until they log out. The page you are redirected to depends on your user type.
    """
    form = LoginForm()
    if request.method == "GET":
        return render_template("auth/login.html", form=form)
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        validated_user = Account.verify_password(username, password)
        if not validated_user:
            return render_template("auth/login.html", form=form)
        # store the user id in a new session and return to the index
        session.clear()
        session["user_id"] = validated_user["ID"]
        try:
            session["user_type"] = validated_user["UserType"]
        except:
            session["user_type"] = None
            requests.put("http://127.0.0.1:8080/bookings/cancel/passed/return/time?customer_id={}".format(str(session["user_id"] )))
        return redirect(url_for("home.index"))

@auth.route("/logout")
def logout():
    """This is to log out. It clears the current session."""
    session.clear()
    return redirect(url_for("home.index"))

@auth.route("/register", methods=("GET", "POST"))
def register():
    """
    Register a new user. Validates that the username is not already taken. Hashes the password for security in another function. The form code is is forms.py.
    """
    form = RegisterForm()
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        firstname = request.form["firstname"].strip()
        lastname = request.form["lastname"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        account = Account(username, password, email, firstname, lastname, phone)
        if account.validate_new_account():
            account.register_account()
            if session.get("user_type") == "Admin":
                return redirect(url_for("admin.user_view"))
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form, user_type=session.get("user_type"))

def login_required(view):
    """This redirects anonymous users to the login page when they try to access a page when not logged in."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view

@auth.before_app_request
def load_logged_in_user():
    """
    If a user id is stored in the session, load the user object from
    the database into ``g.user``.
    """
    user_id = session.get("user_id")
    user_type = session.get("user_type")
    if user_id is None:
        g.user = None
    else:
        if user_type is None:
            g.user = requests.get("http://127.0.0.1:8080/customers/read?id={}".format(str(user_id))).json()[0]
            g.type = "Customer"
        elif user_type == "Admin":
            g.user = requests.get("http://127.0.0.1:8080/staffs/read?user_type=admin").json()[0]
            g.type = user_type
        elif user_type == "Manager":
            g.user = requests.get("http://127.0.0.1:8080/staffs/read?user_type=manager").json()[0]
            g.type = user_type
        elif user_type == "Engineer":
            g.user = requests.get("http://127.0.0.1:8080/staffs/read?user_type=engineer").json()[0]
            g.type = user_type

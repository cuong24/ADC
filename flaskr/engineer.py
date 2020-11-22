#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engineer.py defines the control logic for all the pages the engineer has access to.
"""
from flask import Blueprint, flash, g, redirect
from flask import render_template, request, url_for
from auth import login_required
import requests
import json

engineer = Blueprint("engineer", __name__)

@engineer.route("/backlogs", methods=("GET", "POST"))
@login_required
def backlog_view():
    """
    This displays all cars requiring repairs. It only responds to GET requests.
    """
    if g.type != "Engineer":
        return "Access Denied"
    if request.method == "GET":
        backlogs = requests.get("http://127.0.0.1:8080/backlogs/get/all").json()
        return render_template("engineer/backlog_view.html", backlogs=backlogs)

@engineer.route("/location", methods=("GET", "POST"))
@login_required
def location_map():
    """
    Given a car and location identifier, this returns a map for the engineer to follow. Parameters:
    
    car_id: the id of the car we're looking for
    location_id: The id of the location the car is at
    
    Returns a HTML render containing a map.
    """
    if g.type != "Engineer":
        return "Access Denied"
    car = requests.get("http://127.0.0.1:8080/cars/read?id=" + request.args['car_id']).json()[0]
    location = requests.get("http://127.0.0.1:8080/locations/get?id=" + request.args['location_id']).json()[0]
    return render_template("engineer/location_map.html", car=car, location=location)

@engineer.route("/close/backlog", methods=("POST",))
@login_required
def close_backlog():
    """
    This allows the engineer to mar a cr as repaired, making it available once again. Parameters:
    
    car_id: The id of the car that was repaired.
    
    Once done, it redirects the user back to the engineer home page.
    """
    if g.type != "Engineer":
        return "Access Denied"
    requests.put(
        "http://127.0.0.1:8080/backlogs/close?backlog_id={}&signed_engineer_id={}"
        .format(request.args['backlog_id'], g.user['ID'])
    )
    backlog_left =  requests.get(
        "http://127.0.0.1:8080/backlogs/get/engineer/id?car_id={}"
        .format(request.args['car_id'])
    ) != "No engineer found"
    if not backlog_left:
        requests.put(
            "http://127.0.0.1:8080/cars/update?id={}&status=Available"
            .format(request.args['car_id'])
        )
    return redirect(url_for("engineer.backlog_view"))

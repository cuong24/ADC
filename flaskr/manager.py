#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manager.py is where we define all the control logic for pages the manager can use. 
"""
from flask import Blueprint, g, redirect, render_template
from flask import request, url_for
from auth import login_required
import requests

manager = Blueprint("manager", __name__)

@manager.route("/dashboard", methods=("GET",))
@login_required
def manager_dashboard():
    """
    This is the manager dashboard. They can select one of three graph types to display.
    """
    if g.type != "Manager":
        return redirect(url_for("home.index"))
    if request.method == "GET":
        return render_template("manager/manager_dashboard.html")

@manager.route("/bar_chart", methods=("GET",))
@login_required
def bar_chart():
    """
    This displays the Most Booked Cars bar chart.
    """
    if g.type != "Manager":
        return redirect(url_for("home.index"))
    data = requests.get("http://127.0.0.1:8080/bookings/get/data").json()
    max_value = requests.get("http://127.0.0.1:8080/bookings/get/longest/duration").text
    return render_template('manager/bar_chart.html', title='Most booked cars in minutes', max=max_value, data=data)

@manager.route("/line_chart", methods=("GET", "POST"))
@login_required
def line_chart():
    """
    This displays the Gross Profit by Date line chart.
    """
    if g.type != "Manager":
        return redirect(url_for("home.index"))
    data = requests.get("http://127.0.0.1:8080/bookings/get/profit/data").json()
    max_value = requests.get("http://127.0.0.1:8080/bookings/get/most/profit").text
    return render_template('manager/line_chart.html', title='Profit by date', max=max_value, data=data)

@manager.route("/pie_chart", methods=("GET",))
@login_required
def pie_chart():
    """
    This displays the Most Repaired Cars pie chart.
    """
    if g.type != "Manager":
        return redirect(url_for("home.index"))
    pie_colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
    data = requests.get("http://127.0.0.1:8080/backlogs/get/data").json()
    return render_template('manager/pie_chart.html', title='Most repaired cars', max=20, data=data, colors=pie_colors)

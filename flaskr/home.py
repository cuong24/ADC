#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
home.py defines which page is the home page for different user types.
"""
from flask import Blueprint, g, redirect, url_for
from auth import login_required

home = Blueprint("home", __name__)

@home.errorhandler(404)
def page_not_found(e):
    """
    This is an error handler for 404 page not found errors.
    """
    return "Page not found"

@home.route("/", methods=("GET", "POST"))
@login_required
def index():
    """
    This redirects different user types to their respective home pages after they log in.
    """
    if (g.type == "Admin"):
        return redirect(url_for("admin.car_view"))
    if (g.type == "Engineer"):
        return redirect(url_for("engineer.backlog_view"))
    if (g.type == "Manager"):
        return redirect(url_for("manager.manager_dashboard"))
    return redirect(url_for("customer.car_view"))



    

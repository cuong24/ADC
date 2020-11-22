#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flask import Flask
from admin import admin
from customer import customer
from engineer import engineer
from manager import manager
from home import home
from auth import auth

def create_app(test_config=None):
    initate_flask_app()
    register_blueprint()
    update_test_config()
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app

def initate_flask_app():
    """Create and configure an instance of the Flask application."""
    global app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

def register_blueprint():
    app.register_blueprint(customer, url_prefix="/customer")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(engineer, url_prefix="/engineer")
    app.register_blueprint(manager, url_prefix="/manager")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(home)

def update_test_config(test_config=None):
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

if __name__ == "__main__":
    app = create_app()
    app.run()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
car.py hold the various alidation functions applied to cars.
"""
from flask import flash
import requests

class Car():
    """
    This class holds all the functions in this file.
    """
    def __init__(self, brand, car_type, color, seat, cost, location_id, mac_address="", status = "Available"):
        self.brand = brand
        self.car_type = car_type
        self.color = color
        self.seat = seat
        self.cost = cost
        self.mac_address = mac_address
        self.status = status
        self.location_id = location_id

    @staticmethod
    def validate_cost(cost):
        """
        Cost must be possible to convert into a float ( 3.002 is OK, 'yellow' in not") and also has to be between 1 and 1000. Cars should not rent for less than 1$ or more than 1000$ per hour. Mostly this is to prevent typos. 
        
        Returns False if there's a problem, otherwise True.
        """
        if cost:
            try:
                cost = float(cost)
                if cost > 1000 or cost < 1:
                    flash("Cost must be between 1 and 1000.")
                    return False
            except: 
                flash("Cost must be a number")
                return False
        return True

    @staticmethod   
    def validate_location_id(location_id):
        """
        Makes sure the location id is an integer. These integers map to locations, e.g. 1 = office parking lot, 2 = downtown mall parking lot.
        
        Returns True if it's an integer, otherwise False.
        """
        if location_id:
            try:
                location_id = int(location_id)
            except: 
                flash("Location id must be a number")
                return False
        return True

    def validate_new_car(self):
        """
        A helper function that combines cost and location validation.
       
        Returns True if both pass, otherwise False.
        """
        if Car.validate_cost(self.cost) and Car.validate_location_id(self.location_id):
            return True
        return False

    def validate_update_car(self):
        """
        Another helper function combining cost and location validation, this time specifically for the update form.
        
        Returns True if both pass, otherwise False.
        """
        if self.cost != "" and not Car.validate_cost(self.cost):
            return False
        return Car.validate_location_id(self.location_id)

    def create_car(self):
        """
        Creates a new car.
        """
        requests.post(
            "http://127.0.0.1:8080/cars/create?" +
            "mac_address=" + self.mac_address +
            "&brand=" + self.brand + 
            "&type=" + self.car_type +
            "&location_id=" + self.location_id +
            "&status=Available" + 
            "&color=" + self.color +
            "&seat=" + self.seat +
            "&cost=" + self.cost
        )
        flash("New car created!")

    def update_car(self, car_id):
        """
        Updates an existing car.
        """
        requests.put(
            "http://127.0.0.1:8080/cars/update?" +
            "mac_address=" + self.mac_address +
            "&brand=" + self.brand + 
            "&type=" + self.car_type +
            "&location_id=" + self.location_id +
            "&status=" + self.status +
            "&color=" + self.color +
            "&seat=" + self.seat +
            "&cost=" + self.cost +
            "&id=" + car_id

        )
        flash("Car updated!")

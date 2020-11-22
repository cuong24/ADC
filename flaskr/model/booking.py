#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
booking.py holds all the validators used for bookings.
"""
from flask import flash
from datetime import datetime, timedelta

class Booking():
    """
    This class holds al lthe functions in this file.
    """
    def __init__(self, car_id, customer_id, rent_time, return_time, totalCost):
        self.car_id = car_id
        self.customer_id = customer_id
        self.rent_time = rent_time
        self.return_time = return_time
        self.totalCost = totalCost
        self.status = 'Booked'
        
    @staticmethod
    def validate_date(start_date, end_date):
        """
        Make sure the start date is before the end date. Booking for negative times would charge negative fees and that would be very bad.
        
        Returns False if the dates are nonsensical, True if they are OK.
        """
        if (end_date - start_date).days < 0:
            flash("End date must be later than start date.")
            return False
        if start_date < datetime.now():
            flash("Start date can not been sooner than today")
            return False
        if (end_date - start_date) < timedelta(days = 1):
            flash("Duration must be at least 1 day")
            return False
        return True

    @staticmethod
    def validate_cost(cost):
        """
        Make sure any time someone enters a cost, that it can be cleanly converted to a float. It doesn't have to be an integer, e.g. 5.003 is a valid entry but 'yellow' is not.
        
        Returns True if the cost can be cleanly converted to a float, False otherwise.
        """
        if cost:
            try:
                cost = float(cost)
            except: 
                flash("Cost must be a number.")
                return False
        return True
        
    @staticmethod
    def validate_booking_input(cost, start_date, end_date):
        """
        This is a helper function that combines cost and date validation.
        
        Returns True if both pass, otherwise returns False.
        """
        if Booking.validate_date(start_date, end_date):
            if Booking.validate_cost(cost):
                return True
        return False

    

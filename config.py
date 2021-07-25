# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 13:29:54 2019

@author: Satan
"""

import numpy as np

#=============================================
#   GLOBAL CONSTANTS
#=============================================

POWER_OFF = 0.1          #A x 5V
POWER_ON = 61               # Watt lamp

LANTERN_SEPARATION = 60     # Always between 50 and 100 meters. Mostly 50
                            # Measured 60 m on Google Earth.
DETECTION_RANGE = 1         # Sensor assumed to detect also 1 meter to left 
                            # and right.
SENDING_RADIUS = 2          # "Hop-ranage"
FORWARD_RANGE = 2           # Amount of lamps to turn on in front of car.
BACKWARD_RANGE = 2          # Amount of lamps to turn on behind the car.

TIME_BETWEEN_LAMPPOSTS = 5  # Slowest reasonable time it takes to travel to next node
DIRECTION_TIMEOUT = TIME_BETWEEN_LAMPPOSTS * (SENDING_RADIUS*3)
                            # The maximum time between two detections to
                            # associate them with the same object and use for
                            # direction detection.

#=============================================
#   GLOBAL PARAMETERS
#=============================================

urban = True
dt = 0.01
packet_rate = 0.01

end = 60                  # End of simulation in seconds. One hour.

number_of_sensors = 20

on_time = 5                 # Time from last relevant detection to stay on.

#=============================================
#   SHARED VARIABLES
#=============================================

time = 0
sensors = []
cars = []
spawn_list = []

def init():    
    """Only resets the sensors variable."""
    global sensors, cars, spawn_list, time
    sensors = []
    cars = []
    spawn_list = []
    time = 0
    
variant = np.array([0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.25, 0.3, 0.4,
           0.5, 0.6, 0.7, 0.8, 0.9, 1.0]) # Define the variant that is going to be used.
# Density factor is a scalar that varies the traffic intensity, so the amount 
# of cars that pass a certain point within a certain time interval.
density_factor=variant
current_density_factor = density_factor[0]
# TODO: Take a look at this still
# Variant could be on_time. In that case, uncomment next line
#on_time= variant

    
    
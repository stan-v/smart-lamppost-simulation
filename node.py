# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 19:26:35 2018

@author: Stan

This module defined the SensorNode class which represents one sensor within a 
wireless Sensor Network
"""

# Importing our main log function: the 10 base log.
from math import log10 as log
import numpy as np
import click

import config

from config import (TIME_BETWEEN_LAMPPOSTS, DIRECTION_TIMEOUT,
                    DETECTION_RANGE, SENDING_RADIUS, FORWARD_RANGE,
                    BACKWARD_RANGE)

#=============================================
#   GLOBAL CONSTANTS
#=============================================

BLE = 1

OFF = 0
ON = 1

#=============================================
#   GLOBAL PARAMETERS
#=============================================

# Simple model for BLE
def loss_ble_simple(d):
    '''
    d   -- distance in meter
    '''
    return 40.04 + 10*3.71*log(d)


#=============================================
#   COMMUNICATION CALCULATED PARAMETERS
#=============================================

# The BLE range does not depend on anything (only sensitivity and loss_model)
#ble_range = 111.5

# We can use LoRa SE9 or higher for the whole domain. 

def calc_toa_ble(PL=10, SF=0):
    '''
    BLE has a protocol which sends 14 bytes of overhead along with the actual
    payload. The information is modulated on a 1 MBit/s speed, which gives a 
    Time on air of 1 microsecond per bit or 8 microsecond per byte/octet. 
    ''' 
    amount_of_bytes = 14 + PL
    T = amount_of_bytes*8/10**6
    return T

class SensorNode():
    '''
    The SensorNode class represents a sensor or cluster-head.
    It can transmit data or act as a cluster-head depending on the keyword
    argument is_head. It also tracks its energyconsumption to be summed and 
    compared at the end of a simulation.
    '''
    
    def __init__(self,node_id, x, y, is_head=False, transmission_mode=0,
                 packet_rate=0.01):
        self.node_id = node_id
        self.loc = np.array([x,y])
        self.state = OFF
        self.last_detection = -1000
        self.is_head = is_head
        self.transmission_mode = transmission_mode
        self.task_queue = [(self.poll_sensor,0), (self.evaluate_led_status,0)]
        # Define the list of messages that are received or need to be transmitted
        self.energy_cons = 0
        self.packet_rate = packet_rate
       
        
        
    def tick(self, dt):
        # TODO: Implement cost function and energy tracking.
        #Add the energy consumption to the tracking variables.
        if self.state == ON:
            self.energy_cons += config.POWER_ON * dt
        else:
            self.energy_cons += config.POWER_OFF * dt
        self.poll_sensor()
        self.check_task()
        
    
    def add_task(self,func,over):
        for i,e in enumerate(self.task_queue):
            if config.time+over < e[1]:
                self.task_queue.insert(i,(func,config.time+over))
                return
        else:
            self.task_queue.append((func,config.time+over))
    
    def check_task(self):
        """
        Check whether the first element has occured. Will trigger again as long
        as the first elements time is past.
        """
        if self.task_queue[0][1] <= config.time:
            func,_ = self.task_queue.pop(0)
            if func: func()
            self.check_task()
      
    def poll_sensor(self):
        cars = config.cars
        for car in cars:
            if np.linalg.norm(car.loc - self.loc) < DETECTION_RANGE:
                self.on_detection()
#                self.add_task(self.poll_sensor,TIME_BETWEEN_LAMPPOSTS)
                return
#        else: 
#            self.add_task(self.poll_sensor,config.dt)
    
    def on_detection(self):
        """
        Called when a detection has occurred. 
        This function must: 
            - update its last_detection status;
            - send messages to adjacent nodes;
        It is NOT responsible for turning on its own LED. This happens in the 
        check_led function.
        """
        # TODO: Detection callback
        self.last_detection = config.time
        click.echo(f'[NODE] Node #{self.node_id} detected: T={config.time:.2f}')
             
        
    def evaluate_led_status(self):
        # Check adjacent nodes for relevant detections.
        for i in range(max(self.node_id -1,0), min(self.node_id+2, len(config.sensors)-1)):
            if config.time - config.sensors[i].last_detection < TIME_BETWEEN_LAMPPOSTS:
                self.state = ON
                self.add_task(self.evaluate_led_status,TIME_BETWEEN_LAMPPOSTS)
                return
        # Check left for approaching
        if self.node_id >=3 :
            if (   config.time- config.sensors[self.node_id-2].last_detection 
                < TIME_BETWEEN_LAMPPOSTS
                    and
                0<config.sensors[self.node_id-2].last_detection
                - config.sensors[self.node_id-3].last_detection
                < DIRECTION_TIMEOUT):
                
                self.state = ON
                self.add_task(self.evaluate_led_status,TIME_BETWEEN_LAMPPOSTS)
                return
        # Check right for approching
        if self.node_id < config.number_of_sensors - 3:
            if (   config.time- config.sensors[self.node_id+2].last_detection 
                < TIME_BETWEEN_LAMPPOSTS
                    and
                0<config.sensors[self.node_id+2].last_detection
                - config.sensors[self.node_id+3].last_detection
                < DIRECTION_TIMEOUT):
                self.state = ON
                self.add_task(self.evaluate_led_status,TIME_BETWEEN_LAMPPOSTS)
                return
            
        self.state = OFF
        self.add_task(self.evaluate_led_status,config.dt)
        
    
if __name__=='__main__':
    pass
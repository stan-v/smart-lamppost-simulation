# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 12:37:01 2019

@author: Satan
"""

import numpy as np
import network
import config
from car import Car

default_velocity = 30/3.6       # Standard velocity is 30 km/h

LEFT = -network.width/2-network.cell_width


def car_train(interval):
    for time in np.arange(0,network.end, interval):
        car = Car(-network.width/2-network.cell_width, default_velocity,1)    
                    # Car to right @ 30 km/h 
        config.spawn_list.append((car,time))
        
def random_chance(chance):
    for time in np.arange(0,config.end, 0.1):
        r = np.random.random()
        if r < chance:
            car = Car(((r<chance/2)*2-1)*
                      LEFT, 
                      default_velocity,
                      ((r<chance/2)*2-1))
            config.spawn_list.append((car, time))
            
def random_amount_oneway(amount):
    old_car_amount = int(network.width/(100/3.6)*amount/config.end)
    old_locs = np.random.random(old_car_amount)*network.width-network.width/2
    for loc in old_locs:
        car = Car(loc, 100/3.6,1)
        config.spawn_list.append((car,0))

    times = np.random.random(amount)*config.end
    for time in sorted(times):
        car = Car(LEFT, 100/3.6,1)
        config.spawn_list.append((car,time))
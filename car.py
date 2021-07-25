# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:39:46 2019

@author: Satan
"""

import numpy as np
import network

class Car():
    def __init__(self, x, v, direction):
        self.loc = np.array([x,0.0])
        self.v = v                      # Velocity in m/s
        self.direction = direction      # Either +1 or -1. 0 default.

    def tick(self,dt):
        self.loc += np.array([self.direction * self.v*dt,0])
        
        if abs(self.loc[0]) > network.width/2*1.5:
            self.despawn()
    
    def despawn(self):
        network.despawn_vehicle(self)
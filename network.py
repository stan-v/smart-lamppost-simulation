#!"C:\Users\Satan\Informatica\Python\sci-env\Scripts\python.exe"
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 19:30:17 2018

@author: Stan

This module defines and models the network. It contains a list of nodes and can
graphically represent those.

Requirements: 
    - Energy consumption: star network??
    - Cluster head communicates over LoRa to base
    - Show differences in energy consumption.
    - Transmit power of 0 dBm (1 mW)
    - Payload 10 Bytes for sensors and 60 for Cluster Heads
    - Frequencies: 868 MHz for LoRa and 2.4GHz for BLE

"""


# Python imports

import click
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow
import numpy as np
from functools import partial
from pygame import mixer

import config

# Project imports
from node import (SensorNode, BLE, ON)

mixer.init()
mixer.music.load("mario_1-up_mushroom.mp3")


#=============================================
#   GLOBAL PARAMETERS
#=============================================


width = (config.number_of_sensors-1) * config.LANTERN_SEPARATION  
                    # Dimensions of the network. 10 sensors, so 9 times 
                    # internal distance.
height = 0
cell_width = config.LANTERN_SEPARATION
cell_height = 0

import traffic
    
#=============================================
#   NETWORK & TRAFFIC GENERATION FUNCTIONS
#=============================================

def create_star():
    '''
    The standard network with constant separation between nodes.
    '''
    sens = []
    x_locs = np.linspace(-width/2,width/2, config.number_of_sensors)
    y_locs = np.zeros(1)
    
    for i,x in enumerate(x_locs):
        for y in y_locs:
            sens.append(SensorNode(i,x,y, transmission_mode=BLE, packet_rate=config.packet_rate))
    return sens


def spawn_vehicles():
    """
    Is called every tick. May or may not return a car to spawn and append to
    the traffic list.
    return: a Car or None. 
    """
    for i,(car, time) in enumerate(config.spawn_list):
        if config.time > time:
            config.spawn_list.pop(i)
            config.cars.append(car)
            
        
def despawn_vehicle(car):
    config.cars.remove(car)
            
    

#=============================================
#   ANALYSIS FUNCTIONS
#=============================================

circles = []
car_circs = []
sim_fig,sim_ax = None,None

def sim_vis():
    global sim_fig,sim_ax
    sim_fig,sim_ax = plt.subplots()
    circles.clear()
    car_circs.clear()
    for sensor in config.sensors:
        circle = Circle(xy=sensor.loc, radius=5, color='grey')
        circles.append(circle)
        sim_ax.add_artist(circle)
    
    for car,_ in config.spawn_list:
        circle2 = Circle(xy=car.loc,radius=2,color='blue')
        car_circs.append(circle2)
        sim_ax.add_artist(circle2)
    
    sim_ax.set_xlim((-width-cell_width, width+cell_width))
    sim_ax.set_ylim((-width/3, width/3))
    sim_ax.set_aspect('equal')
    
    
def update_plot():
    for sensor, circle in zip(config.sensors, circles):
        circle.set_color('red') if sensor.state == ON else circle.set_color('grey')
    
    for car,circle in zip(config.cars, car_circs):
        circle.center = tuple(car.loc)
    
    plt.title((f'Time = {config.time:.1f}'))
    #plt.show()
    sim_fig.canvas.draw()
    sim_fig.canvas.flush_events()

def visualize():
    """
    Plots the nodes. Not the clusterheads yet. Fix if needed
    """
    fig, ax = plt.subplots()
    sensors = config.sensors
    
    plt.axis('equal')
   
    # Plot sensors
    xs = np.array([sensor.loc[0] for sensor in sensors])
    ys = np.array([sensor.loc[1] for sensor in sensors])
    heads = np.array([True if sensor.is_head else False for sensor in sensors])
    bles = np.array([1 if sensor.transmission_mode==BLE else 0 for sensor in sensors])
    
    plt.plot(xs[(heads==False) & (bles==True)],
            ys[(heads==False) & (bles==True)], 'b.')
    

    # Plot cross        
#    plt.plot([-width/2,width/2], [0,0], 'y')
#    plt.plot([0,0], [-height/2, height/2], 'y')
    # Plot border
#    plt.plot([-width/2, width/2, width/2,-width/2,-width/2],
#             [-height/2,-height/2,height/2,height/2,-height/2], linewidth=3)    
    
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.title(f'Map of Lamppost nodes')
    
    #plt.legend(('BLE-enabled sensors', 'LoRa7 sensors', 'LoRa 8 sensors', 'Cluster-heads'))
    plt.show()
    
    
    
# =============================================================================
# def calc_range(func, threshold):
#     '''
#     Calculates the highest distance in meters for which lora is below the 
#     threshold.
#     '''    
#     d = 500
#     # Establish upper bound
#     while func(d) < threshold:
#         d *= 2
#     max_d = d
#     min_d = 0
#     d = (min_d+max_d)/2
#     while max_d-min_d > 1:
#         if func(d) > threshold:
#             max_d = d
#             
#         else:
#             min_d = d
#         d = (min_d+max_d)/2
#     return np.floor(min_d)
# =============================================================================
        

def plot_set(setname):
    
    # !!! Legend does not match
    
    data_star_urban = extract_data(setname)
    
    #Markers: s(quare) for urban ^ for rural green for smart, red for star
    
    if data_star_urban: 
        # normal total je weet zelf.
        normal_total = config.end*config.POWER_ON*config.number_of_sensors
        plt.plot(config.density_factor*2262, 100-(data_star_urban[0]/normal_total*100), 'rs')
        plt.plot(plt.xlim(), [100]*2, 'r--')
        
    plt.title(f"Energy savings (simulated for 60 seconds)")
    plt.xlabel('Cars per hour')
    plt.ylabel('Energy saved (%)')
    plt.show()

def extract_data(setname):
    prefix = setname + '/sim_'
    total_energy = np.zeros(len(config.density_factor))
    try:
        for i in range(len(config.density_factor)):
            print(f'Loading {prefix+str(i)}.npz...')
            arc = np.load(prefix+str(i)+'.npz')
            cons = arc.f.result
    #        bles,heads =  arc.f.bles, arc.f.heads
            total_energy[i] = np.sum(cons)
        
        return total_energy,
    except:
        return None
    
def plot_energy(setname):
    """
    Plots the energy of a given situation compared to a single variant.
    Total energy is extracted by the given setname.
    """
    
    total_energy, = extract_data(setname)
        
    plt.plot(config.density_factor, total_energy, 'r.')
    plt.title(f"Energy consumptions various traffic densities")
    plt.xlabel('Variant')
    plt.ylabel('Energy (J)')


def simulate(urban=False, vis=False):
    '''
    Simulates one run of the program and returns arrays of data
    '''
    dt = config.dt
    t = 0
    try:
        while config.time < config.end:
            for sensor in config.sensors:
                sensor.tick(dt)
            for car in config.cars:
                car.tick(dt)
            spawn_vehicles()
            if not t%10 and vis: update_plot()
            config.time += dt
            t += 1
    except KeyboardInterrupt:
        print('Simulation aborted!')
    return np.array([sensor.energy_cons for sensor in config.sensors])
    
    
def show_energy_consumption(cons):
    plt.figure()
    sensors = config.sensors
    bles = np.array([1 if sensor.transmission_mode==BLE else 0 for sensor in sensors])
    heads = np.array([sensor.is_head for sensor in sensors])
    
    plt.plot(np.arange(len(cons))[bles==1],cons[bles==1] , 'b.')    
    plt.plot(np.arange(len(cons))[heads==1], cons[heads==1] , 'ro', fillstyle='none') 
    plt.plot(np.arange(len(cons))[(bles==0)],cons[(bles==0)] , 'g.')  
    
    plt.plot(plt.xlim(), [config.end*config.POWER_ON]*2, 'r--')
    
    plt.title('Consumed energy per node')
    plt.xlabel('Node ID')
    plt.ylabel('Total consumed energy in J')
    plt.legend(['Lampposts', 'Always-on-consumption'])
    
    #head_avg = np.mean(cons[heads])
    node_avg = np.mean(cons[heads==False])
    normal_total = config.end*config.POWER_ON*config.number_of_sensors
    percentage = np.sum(cons)/normal_total * 100
    #print(f'Average energy consumption of cluster heads: {head_avg} J')
    print(f'Average energy consumption of nodes: {node_avg} J')   
    print(f'Energy consumption: {np.sum(cons):.2f} / {normal_total} ({percentage:.1f}%)J')
    

def show_energy_consumption_from_file(fname):
    arc = np.load(fname)
    cons,bles,heads = arc.f.result, arc.f.bles,arc.f.heads
    plt.plot(np.arange(len(cons))[bles==1],cons[bles==1] , 'b.')   
    plt.plot(np.arange(len(cons))[heads==1], cons[heads==1] , 'ro', fillstyle='none') 
    plt.plot(np.arange(len(cons))[(bles==0) ],cons[(bles==0)] , 'g.')  
    
    plt.plot(plt.xlim(), [config.end*config.POWER_ON]*2, 'r--')
    
    plt.title('Consumed energy per node')
    plt.xlabel('Node ID')
    plt.ylabel('Total consumed energy in J')
    plt.legend(('BLE nodes'))
    

    node_avg = np.mean(cons[heads==False])
    normal_total = config.end*config.POWER_ON*config.number_of_sensors
    percentage = np.sum(cons)/normal_total * 100
    print(f'Average energy consumption of nodes: {node_avg} J')   
    print(f'Energy consumption: {np.sum(cons):.2f} / {normal_total} ({percentage:.1f}%)J')
    
#def save_consumption(filename):
#    sensors = config.sensors
#    head_cons = np.array([sensor.energy_cons for sensor in sensors if sensor.is_head])
#    node_cons = np.array([sensor.energy_cons for sensor in sensors if not sensor.is_head])
#    np.savez(filename, head_cons=head_cons, node_cons=node_cons)


@click.command()
@click.option('--vis', is_flag=True, default=False, help='Creates a map of the nodes')
@click.option('--sim', is_flag=True, default=False, help='Run a Simulation')
@click.option('--cons-vis', is_flag=True, default=False, help='Plots the '
                 + 'consumption of the simulation. Must be used with --sim')
@click.option('--set','_set', default=None, help='Selects a set to operate on')
def cli(vis, sim, cons_vis, _set):
    for i in range(len(config.density_factor)):
        config.current_density_factor = config.density_factor[i]
        run_sim(vis, sim,cons_vis, _set, i)
    
    mixer.music.play()



def run_sim(vis, sim, cons_vis, _set, i):
    config.init()
    config.sensors = create_star()
    traffic.random_amount_oneway(int(2262/3600*config.end*config.current_density_factor))
    
    
    if sim:
        if vis:
            sim_vis()
        
        name = 'sim_'
        result = simulate(vis=vis)
        name += str(i)
        
        bles = np.array([1 if sensor.transmission_mode==BLE else 0 for sensor in config.sensors])
        heads = np.array([sensor.is_head for sensor in config.sensors])
        
        np.savez(name, result=result, bles=bles, heads=heads)
            
    if vis:
        if _set:
            plot_set(_set)
        elif not sim: 
            visualize()
    if cons_vis:
        #Visualize consumption. Must be used in conjunction with sim.
        show_energy_consumption(result)

    
    # result,bles,sf7s,heads = arc.f.result, arc.f.bles, arc.f.sf7s, arc.f.heads

if __name__ == '__main__':
    cli()
    
    
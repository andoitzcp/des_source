# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 17:37:23 2022

@author: andoi
"""

import simpy
import random
import pandas as pd
from numpy import random as nprng
import csv

rng = nprng.default_rng()

#Global class cantaining the system common variables
class g:
    DURATION = 960 #Duration of the simulation in minutes (16 hours)
    RUNS = 20
    
    GAS_STATION_QTY = 4 #units
    PARKING_CAPACITY = 100 #units
    P_REFILL = 0.5 #Chance a car might refill it's tank at the gas station
    
    DRIVE_LONG = (25, 1) #(Mean, S.Deviation) in minutes. Normal distribution.
    DRIVE_SHORT = (3, 1) #(Mean, S.Deviation) in minutes. Normal distribution.
    SEARCH_PARKING = (15, 8) #(Mean, S.Deviation) in minutes. Normal distribution.
    REFILL = (4, 1) #(Mean, S.Deviation) in minutes. Normal distribution.
    
    INTER_ARRIVAL = (1, 15) #exponential interarrival times for (A, B) populations in minutes
    PARKING_A = (2, 5) #(Alpha, Beta) in minutes. Beta distribution.
    PARKING_B = (2, 5) #(Alpha, Beta) in minutes. Beta distribution.
    
# Defines attributes of car class, the dynamic entity moving through the model.
class car:
    def __init__(self, car_id, driver_type):
        self.id = car_id
        self.type = driver_type #Either worker (A) or casual (B).

#Contains the simulation model itself.
class example_model:
    def __init__(self, number_of_runs):
        self.env = simpy.Environment()
        
        self.car_counter = 0
        
        self.number_of_runs = number_of_runs
        
        #Defining the resources
        self.res_gs = simpy.Resource(self.env, capacity=g.GAS_STATION_QTY)
        self.res_pc = simpy.Container(self.env, init=0, capacity=g.PARKING_CAPACITY)
        
    def car_generator_A(self):
        while self.env.now < 120:
            car_gen = car(self.car_counter, 'A')
            self.car_counter += 1
            
            self.env.process(self.main_proc(car_gen))
            
            sampled_interarrival = random.expovariate(1.0/g.INTER_ARRIVAL[0])
            yield self.env.timeout(sampled_interarrival)
            
    def car_generator_B(self):
        while True:
            car_gen = car(self.car_counter, 'B')
            self.car_counter += 1
            
            self.env.process(self.main_proc(car_gen))
            
            sampled_interarrival = random.expovariate(1.0/g.INTER_ARRIVAL[1])
            yield self.env.timeout(sampled_interarrival)
    
    def main_proc(self, car_ent):
        time_record = []
        time_record.append(self.env.now)
        
        drive_long_time = rng.lognormal(g.DRIVE_LONG[0], g.DRIVE_LONG[1])
        yield self.env.timeout(drive_long_time)
        
        time_record.append(self.env.now)
        
        # if random.uniform(0,1) > 0:
        #     refill_time = random.normalvariate(g.REFILL[0], g.REFILL[1])
        #     with self.res_gs.request() as req_gs:
        #         yield req_gs
        #         yield self.env.timeout(refill_time)
                
        # time_record.append(self.env.now)
                
        # drive_short_time = random.normalvariate(g.SEARCH_PARKING[0], g.SEARCH_PARKING[1])
        # yield self.env.timeout(drive_short_time)
        
        # time_record.append(self.env.now)
        
        # if self.res_pc.level > 100:
        #     search_parking_time = random.normalvariate(g.DRIVE_LONG[0], g.DRIVE_LONG[1])
        #     yield self.env.timeout(search_parking_time)
        # else:
        #     yield self.res_pc.put(amount=1)
            
        # time_record.append(self.env.now)
        
        # if car_ent.type == 'A':
        #     parking_time = random.betavariate(g.PARKING_A[0], g.PARKING_A[1])
        # else:
        #     parking_time = random.betavariate(g.PARKING_B[0], g.PARKING_B[1])
            
        # yield self.env.timeout(parking_time)

        # time_record.append(self.env.now)
        
        # drive_short_time = random.normalvariate(g.SEARCH_PARKING[0], g.SEARCH_PARKING[1])
        # yield self.env.timeout(drive_short_time)
        
        # time_record.append(self.env.now)
        
        # if random.uniform(0,1) > 0:
        #     refill_time = random.normalvariate(g.REFILL[0], g.REFILL[1])
        #     with self.res_gs.request() as req_gs:
        #         yield req_gs
        #         yield self.env.timeout(refill_time)
                
        # time_record.append(self.env.now)
        
        # drive_long_time = random.normalvariate(g.DRIVE_LONG[0], g.DRIVE_LONG[1])
        # yield self.env.timeout(drive_long_time)
        
        # time_record.append(self.env.now)
        
        print(time_record)
        
    def run(self):
        self.env.process(self.car_generator_A())
        self.env.process(self.car_generator_B())

        self.env.run(until=g.DURATION)

for run in range(g.RUNS):
    print("Run ", run+1, "of ", g.RUNS, sep="")
    my_example = example_model(run)
    my_example.run()
    print()
        
        
        

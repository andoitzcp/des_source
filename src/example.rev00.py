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

# Global class cantaining the system common variables


class g:
    DURATION = 960  # Duration of the simulation in minutes (16 hours)
    RUNS = 20

    GAS_STATION_QTY = 4  # units
    PARKING_CAPACITY = 100  # units
    P_REFILL = 0.5  # Chance a car might refill it's tank at the gas station

    DRIVE_LONG = (8, 3)  # (Shape 'k', Scale 'theta') in minutes. Gamma distribution.
    DRIVE_SHORT = (2, 3, 4)  # (Lower bound, Mode, Upper bound) in minutes. Triangular distribution.
    SEARCH_PARKING = (10, 1)  # (Shape 'k', Scale 'theta') in minutes. Gamma distribution.
    REFILL = (4, 5, 8)  # (Lower bound, Mode, Upper bound) in minutes. Triangular distribution.
    INTER_ARRIVAL = (1, 15)  # exponential interarrival times for (A, B) populations in minutes

    PARKING_A = (560, 60)  # (Mean, S.Deviation) in minutes. Normal distribution.
    PARKING_B = (5, 0.7)  # (Mean, Sigma) in minutes. Lognormal distribution.
    df = pd.DataFrame(columns=['RUN', 'CAR_TYPE', 'HAS_PARKED', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'])

# Defines attributes of car class, the dynamic entity moving through the model.


class car:

    def __init__(self, car_id, driver_type, has_parked):
        self.id = car_id
        self.type = driver_type  # Either worker (A) or casual (B).
        self.has_parked = has_parked

# Contains the simulation model itself.


class example_model:
    def __init__(self, number_of_runs):
        self.env = simpy.Environment()

        self.car_counter = 0
        self.parked_cars = 0

        self.number_of_runs = number_of_runs

        # Defining the resources
        self.res_gs = simpy.Resource(self.env, capacity=g.GAS_STATION_QTY)

        # Defining data stuctures
        self.tmp_lst = []

    def car_generator_A(self):
        while self.env.now < 120:
            car_gen = car(self.car_counter, 'A', True)
            self.car_counter += 1

            self.env.process(self.main_proc(car_gen))

            sampled_interarrival = random.expovariate(1.0/g.INTER_ARRIVAL[0])
            yield self.env.timeout(sampled_interarrival)

    def car_generator_B(self):
        while True:
            car_gen = car(self.car_counter, 'B', True)
            self.car_counter += 1

            self.env.process(self.main_proc(car_gen))

            sampled_interarrival = random.expovariate(1.0/g.INTER_ARRIVAL[1])
            yield self.env.timeout(sampled_interarrival)

    def main_proc(self, car_ent):
        # Defininig temporary dictionary 
        tmp_dict = {"RUN": [], "CAR_TYPE": [], "HAS_PARKED": [],
                    "A": [], "B": [], "C": [], "D": [], "E": [],
                    "F": [], "G": [], "H": [], "I": [], "J": [], "K": []}

        tmp_dict["RUN"].append(self.number_of_runs)
        tmp_dict["CAR_TYPE"].append(car_ent.type)
        tmp_dict["A"].append(self.env.now)

        drive_long_time = rng.gamma(g.DRIVE_LONG[0], g.DRIVE_LONG[1])
        yield self.env.timeout(drive_long_time)

        tmp_dict["B"].append(self.env.now)

        if random.uniform(0, 1) > 0:
            refill_time = rng.triangular(g.REFILL[0], g.REFILL[1], g.REFILL[2])
            with self.res_gs.request() as req_gs:
                yield req_gs
                tmp_dict["C"].append(self.env.now)
                yield self.env.timeout(refill_time)
        else:
            tmp_dict["C"].append(self.env.now)

        tmp_dict["D"].append(self.env.now)

        drive_short_time = rng.triangular(g.DRIVE_SHORT[0], g.DRIVE_SHORT[1], g.DRIVE_SHORT[2])
        yield self.env.timeout(drive_short_time)

        tmp_dict["E"].append(self.env.now)

        if self.parked_cars >= g.PARKING_CAPACITY:
            car_ent.has_parked = False
            search_parking_time = rng.gamma(g.SEARCH_PARKING[0], g.SEARCH_PARKING[1])
            yield self.env.timeout(search_parking_time)
        else:
            self.parked_cars += 1

        tmp_dict["F"].append(self.env.now)

        if car_ent.type == "A":
            parking_time = rng.normal(g.PARKING_A[0], g.PARKING_A[1])
        else:
            parking_time = rng.lognormal(g.PARKING_B[0], g.PARKING_B[1])

        yield self.env.timeout(parking_time)

        if car_ent.has_parked:
            self.parked_cars -= 1

        tmp_dict["G"].append(self.env.now)

        drive_short_time = rng.triangular(g.DRIVE_SHORT[0], g.DRIVE_SHORT[1], g.DRIVE_SHORT[2])
        yield self.env.timeout(drive_short_time)

        tmp_dict["H"].append(self.env.now)

        if random.uniform(0,1) > 0:
            refill_time = rng.triangular(g.REFILL[0], g.REFILL[1], g.REFILL[2])
            with self.res_gs.request() as req_gs:
                yield req_gs
                tmp_dict["I"].append(self.env.now)
                yield self.env.timeout(refill_time)
        else:
            tmp_dict["I"].append(self.env.now)

        tmp_dict["J"].append(self.env.now)

        yield self.env.timeout(drive_long_time)

        tmp_dict["K"].append(self.env.now)
        tmp_dict["HAS_PARKED"].append(car_ent.has_parked)

        self.tmp_lst.append(tmp_dict)
        ##print(car_ent.type, self.parked_cars, time_record)

    def run(self):
        self.env.process(self.car_generator_A())
        self.env.process(self.car_generator_B())

        self.env.run(until=g.DURATION)
        tmp_df = pd.DataFrame(self.tmp_lst)
        g.df = pd.concat([g.df, tmp_df], ignore_index=True)
        g.df.to_csv('out.csv', index=False)
        print(g.df)
        # print(self.tmp_lst)



for run in range(g.RUNS):
    print("Run ", run+1, "of ", g.RUNS, sep="")
    my_example = example_model(run)
    my_example.run()
    print()

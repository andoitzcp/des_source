# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 11:43:32 2022

@author: andoi
"""

import simpy
import random
import pandas as pd
import csv

class g:
    cv_st_qced_inter = 5
    cv_st_dr_inter = 24*31*2
    cv_st_ece54_inter = 24*31
    cv_st_rr_inter = 24
    cv_st_csa_inter = 48
    
    cv_st_qced_req = 3000
    cv_st_dr_req = 6
    cv_st_ece54_req = 8
    cv_st_rr_req = 300
    cv_st_csa_req = 80
    
    mean_enllantado = 15/60
    mean_test_qced = 72
    number_of_indoor_mach = 4
    number_of_rr_mach = 1
    number_of_butler_mach = 1
    number_of_technicians = 1
    number_of_operaries = 1
    sim_duration = 24*365*10
    number_of_runs = 1
    
    number_of_indoor_rims = 16
    number_of_indoor_inventory = 40
    
    shift_duration = 8
    
    
class cv:
    def __init__(self, cv_id, cv_test, cv_client, cv_code):
        self.id = cv_id
        self.test = cv_test
        self.client = cv_client
        self.code = cv_code
        

class lab_model:
    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.cv_counter = 0
        self.item = []
        self.item_2 = []
        self.item_3 = []
        
        self.indoor_mach = simpy.Resource(self.env, capacity=g.number_of_indoor_mach)
        self.rr_mach = simpy.Resource(self.env, capacity=g.number_of_rr_mach)
        self.butler_mach = simpy.Resource(self.env, capacity=g.number_of_butler_mach)
        self.technicians = simpy.PreemptiveResource(self.env, capacity=g.number_of_technicians)
        self.operaries = simpy.Resource(self.env, capacity=g.number_of_operaries)
        self.indoor_rims = simpy.Resource(self.env, capacity=g.number_of_indoor_rims)
        
        self.indoor_inv_store = simpy.Store(self.env, capacity=g.number_of_indoor_inventory)
        self.indoor_rim_store = simpy.Store(self.env, capacity=g.number_of_indoor_rims)
        
    def generate_cv_st_qced_arrivals(self):
        while self.cv_counter<g.cv_st_qced_req:
        
            self.cv_counter += 1
            
            print("cv_counter = ",self.cv_counter)
        
            csq = cv(self.cv_counter, "QCED", "ST", "CV162")
            
            print()
        
            sampled_interarrival = random.expovariate(1.0/g.cv_st_qced_inter)
        
            yield self.env.timeout(sampled_interarrival) & self.indoor_inv_store.put(csq)
            
            print("inv", len(self.indoor_inv_store.items))

    def obstruct_technician(self):
        while True:
            yield self.env.timeout(g.shift_duration)
            
            #print(self.env.now)
            
            with self.technicians.request(priority=-2, preempt=True) as req_tech_oof:
                
                yield req_tech_oof
                
                yield self.env.timeout(24-g.shift_duration)
            
    def rim_proc(self):
        while True:       
    
            with self.butler_mach.request() as req_butler:
                
                yield req_butler
                
                self.item = yield self.indoor_inv_store.get()
                
                print("item_1: ",self.item)
                
                time_left_rim = random.triangular(40, 60, 80)
                
                yield self.env.timeout(time_left_rim)
                
            
            print("a",self.env.now)
            
            print("rim", len(self.indoor_rim_store.items))

    
            yield self.indoor_rim_store.put(self.item)
            
            print("b",self.env.now)
            
            with self.indoor_mach.request() as req_mach:
                
                yield req_mach
                
                self.item_2 = yield self.indoor_rim_store.get()
               # self.item_3 = yield self.indoor_rim_store.get()
                
                print("item_2: ",self.item_2)
                
                time_left_test =random.triangular(100, 120, 180)
                
                yield self.env.timeout(time_left_test)
                
    
    def run(self):
        self.env.process(self.generate_cv_st_qced_arrivals())
        self.env.process(self.obstruct_technician())
        self.env.process(self.rim_proc())

        self.env.run(until=g.sim_duration)
        
for run in range(g.number_of_runs):
    print("Run ", run+1, "of ", g.number_of_runs, sep="")
    my_test_model = lab_model(run)
    my_test_model.run()
    print()

    
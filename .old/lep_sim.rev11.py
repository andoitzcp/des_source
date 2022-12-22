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
        self.cv_gen_current_num = 0

        
        self.indoor_mach = simpy.Resource(self.env, capacity=g.number_of_indoor_mach)
        self.rr_mach = simpy.Resource(self.env, capacity=g.number_of_rr_mach)
        self.butler_mach = simpy.Resource(self.env, capacity=g.number_of_butler_mach)
        self.technicians = simpy.PreemptiveResource(self.env, capacity=g.number_of_technicians)
        self.operaries = simpy.Resource(self.env, capacity=g.number_of_operaries)
        self.indoor_rims = simpy.Resource(self.env, capacity=g.number_of_indoor_rims)
    
        
    def generate_cv_st_qced_arrivals(self):
        while self.csqa<g.cv_st_qced_req:
        
            self.cv_counter += 1
            self.cv_gen_current_num += 1            
        
            csq = cv(self.cv_counter, "QCED", "ST", "CV162")
        
            self.env.process(self.rim_(csq))
        
            sampled_interarrival = random.expovariate(1.0/g.cv_st_qced_inter)
        
            yield self.env.timeout(sampled_interarrival)
            

    def obstruct_technician(self):
        while True:
            yield self.env.timeout(g.shift_duration)
            
            #print(self.env.now)
            
            with self.technicians.request(priority=-2, preempt=True) as req_tech_oof:
                
                yield req_tech_oof
                
                yield self.env.timeout(24-g.shift_duration)
                
    def master_proc(self, cubierta):
        cv_gen_t = self.env.now
        
        yield self.env.process(self.rim_proc())
        
        
            
    def rim_proc(self):
        
        with self.indoor_rims.request() as req_indoor_rim:
            
            yield req_indoor_rim
        
            with self.butler_mach.request() as req_butler:
            
                yield req_butler
        
                time_left_rim = random.triangular(12/60, 25/60, 15/60)

                while time_left_rim > 0:  
        
                    with self.technicians.request(priority=0, preempt=False) as req_tech:
                    
                        yield req_tech & req_butler & req_indoor_rim
            
            
                        try:
                
                            start = self.env.now
                            yield self.env.timeout(time_left_rim)
                            time_left_rim = 0
                
            
                        except simpy.Interrupt:
                
                            time_left_rim -= self.env.now - start
        

    def indoor_cv_selector(self):
        while self.cv_gen_current_num > 0:
            self.cv_gen_current_num -= 2
            
            cv_test_1 = lab_model(run_number).rim_proc()
            
    
    def run(self):
        self.env.process(self.generate_cv_st_qced_arrivals())
        self.env.process(self.obstruct_technician())

        self.env.run(until=g.sim_duration)
        
for run in range(g.number_of_runs):
    print("Run ", run+1, "of ", g.number_of_runs, sep="")
    my_test_model = lab_model(run)
    my_test_model.run()
    print()

    
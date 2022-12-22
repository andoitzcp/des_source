# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 14:32:22 2022

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
    number_of_indoor_mach = 8
    number_of_rr_mach = 1
    number_of_butler_mach = 1
    number_of_technicians = 1
    number_of_operaries = 1
    sim_duration = 24*365
    number_of_runs = 1
    
    number_of_indoor_rims = 16
    
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
        self.csqa = 0
        self.rimmed = 0
        self.indoor_split_counter = 0
        
        self.parada = False

        self.cv_gen = 0
        self.cv_rim = cv("initial", "QCED", "initial", "initial")
        self.cv_test_1 = cv("initial", "QCED", "initial", "initial")
        self.cv_test_2 = cv("initial", "QCED", "initial", "initial")
        
        self.cv_gen_list = []
        self.cv_rim_list = []
        self.test_runned = 0
        
        
        
        self.indoor_mach = simpy.Resource(self.env, capacity=g.number_of_indoor_mach)
        self.rr_mach = simpy.Resource(self.env, capacity=g.number_of_rr_mach)
        self.butler_mach = simpy.Resource(self.env, capacity=g.number_of_butler_mach)
        self.technicians = simpy.PriorityResource(self.env, capacity=g.number_of_technicians)
        self.operaries = simpy.Resource(self.env, capacity=g.number_of_operaries)
        self.indoor_rims = simpy.Resource(self.env, capacity=g.number_of_indoor_rims)
        
        
        self.run_number = run_number
        
        self.results_df_rim = pd.DataFrame()
        self.results_df_rim["CV_ID"] = []
        self.results_df_rim["CV_gen_t"] = []
        self.results_df_rim["CV_rim_start_t"] = []
        self.results_df_rim["CV_rim_end_t"] = []
        self.results_df_rim.set_index("CV_ID", inplace=True)
        
        self.results_df_indoor = pd.DataFrame()
        self.results_df_indoor["CV_ID"] = []
        self.results_df_indoor["CV_mount_start_t"] = []
        self.results_df_indoor["CV_mount_end_t"] = []
        self.results_df_indoor["CV_test_start_t"] = []
        self.results_df_indoor["CV_test_end_t"] = []
        self.results_df_indoor.set_index("CV_ID", inplace=True)
        
        self.results_df = pd.DataFrame()
        self.results_df["CV_ID"] = []
        self.results_df["CV_gen_t"] = []
        self.results_df["CV_rim_start_t"] = []
        self.results_df["CV_rim_end_t"] = []
        self.results_df["CV_ID"] = []
        self.results_df["CV_mount_start_t"] = []
        self.results_df["CV_mount_end_t"] = []
        self.results_df["CV_test_start_t"] = []
        self.results_df["CV_test_end_t"] = []
        self.results_df["CV_rim_q_d"] = []
        self.results_df["CV_rim_proc_d"] = []
        self.results_df["CV_mount_q_d"] = []
        self.results_df["CV_mount_proc_d"] = []
        self.results_df["CV_test_q_d"] = []
        self.results_df["CV_test_proc_d"] = []
        self.results_df.set_index("CV_ID", inplace=True)
        
        
    
    def generate_cv_st_qced_arrivals(self):
        while self.csqa < g.cv_st_qced_req:
        
            self.cv_counter += 1
            self.csqa += 1
            
            num_enllantadas = self.csqa
        
            self.cv_gen = cv(self.cv_counter, "QCED", "ST", "CV162")
            
            self.cv_gen_list.append(self.cv_gen)
            
           #print("cv_gen_length : ", len(self.cv_gen_list))
            
            
            self.env.process(self.master_indoor_proc())
        
            sampled_interarrival = random.expovariate(1.0/g.cv_st_qced_inter)
        
            yield self.env.timeout(sampled_interarrival)
            
            #print(num_enllantadas)
            
    def obstruct_technician(self):
        while True:
            yield self.env.timeout(g.shift_duration)
            
            #print(self.env.now)
            
            with self.technicians.request(priority=-2, preempt=True) as req_tech_oof:
                
                yield req_tech_oof
                
                yield self.env.timeout(24-g.shift_duration)      
                
    def master_indoor_proc(self):
    
        
        if len(self.cv_gen_list) < 1:
            pass
        else:
            yield self.env.process(self.rim_proc(self.cv_rim))
            self.cv_rim = self.cv_gen_list.pop(0)
            #print("rim end : ",self.env.now)
            self.cv_rim_list.append(self.cv_rim)
            #print(self.cv_rim.id, self.cv_rim.test )
            #print("cv_rim_length : ", len(self.cv_rim_list))

        
        if self.indoor_split_counter % 2 == 0:
            self.indoor_split_counter += 1
            #print("ind_split : ", self.indoor_split_counter)
            

            try:
                yield self.env.process(self.mount_proc(self.cv_test_1, self.cv_test_2))
                self.cv_test_1 = self.cv_rim_list.pop(0)
                #print(self.cv_test_1.id, self.cv_test_1.test, len(self.cv_rim_list) )
                self.cv_test_2 = self.cv_rim_list.pop(0)
                #print(self.cv_test_2.id, self.cv_test_2.test, len(self.cv_rim_list) )
                #print("cv_rim_length : ", len(self.cv_rim_list))
            except:
                pass
        else:
            self.indoor_split_counter += 1
                           
    def rim_proc(self, cv_rim):
        
            cv_gen_t = self.env.now
            
            time_left_rim = random.triangular(12/60, 25/60, 15/60)

            while time_left_rim > 0:  
            
                with self.butler_mach.request() as req_butler, self.technicians.request(priority=0, preempt=False) as req_tech:
                    try:
                        start = []
                        
                        yield req_butler & req_tech
                        start.append(self.env.now)

                        yield self.env.timeout(time_left_rim)
                        time_left_rim = 0
                    except simpy.Interrupt():
                        time_left_rim -= self.env.now - start
        
            cv_rim_start_t = start.pop(0)
            print(cv_rim_start_t)
            cv_rim_end_t = self.env.now
                            
            df_to_add_rim = pd.DataFrame({"CV_ID":[self.cv_rim.id],
                                                      "CV_gen_t":[cv_gen_t],
                                                      "CV_rim_start_t":[cv_rim_start_t],
                                                      "CV_rim_end_t":[cv_rim_end_t]})
            df_to_add_rim.set_index("CV_ID", inplace=True)
            self.results_df_rim = pd.concat([self.results_df_rim, df_to_add_rim])
            #print(self.results_df_rim)
    
    def mount_proc(self, cv_test_1, cv_test_2):
        time_left_mount = random.triangular(45/60, 75/60, 180/60)
        
        with self.technicians.request(priority=-1) as req_tech:
        
            yield req_tech
            
            cv_mount_start_t = self.env.now
    
            while time_left_mount > 0:        
                    
                    try: 
            
                        start = self.env.now
                        yield self.env.timeout(time_left_mount)
                        time_left_mount = 0
            
                    except simpy.Interrupt:
        
                        time_left_mount -= self.env.now - start
          
        
        cv_mount_end_t = self.env.now
            
        df_to_add_indoor_1 = pd.DataFrame({"CV_ID":[self.cv_test_1.id],
                              "CV_mount_start_t":[cv_mount_start_t],
                              "CV_mount_end_t":[cv_mount_end_t]})
        df_to_add_indoor_1.set_index("CV_ID", inplace=True)
        df_to_add_indoor_2 = pd.DataFrame({"CV_ID":[self.cv_test_2.id],
                              "CV_mount_start_t":[cv_mount_start_t],
                              "CV_mount_end_t":[cv_mount_end_t]})
        df_to_add_indoor_2.set_index("CV_ID", inplace=True)
        self.results_df_indoor = pd.concat([self.results_df_indoor, df_to_add_indoor_1, df_to_add_indoor_2])
    def cond_proc(self):
            
        yield self.env.timeout(3)
        
    def padj_proc(self):
        
        with self.technicians.request(priority=-3) as req_tech:
        
            yield req_tech
        
            yield self.env.timeout(5/60)
        
    
        cv_test_start_t = self.env.now
        
        sampled_test_duration = random.normalvariate(74.42, 11.11)
            
        yield self.env.timeout(sampled_test_duration)
    
        cv_test_end_t = self.env.now
        
        print(self.cv_test_1.id, self.cv_test_1.test, len(self.cv_rim_list) )
        print(self.cv_test_2.id, self.cv_test_2.test, len(self.cv_rim_list) )
        df_to_add_indoor_1 = pd.DataFrame({"CV_ID":[self.cv_test_1.id],
                              "CV_test_start_t":[cv_test_start_t],
                              "CV_test_end_t":[cv_test_end_t]})
        df_to_add_indoor_1.set_index("CV_ID", inplace=True)
        df_to_add_indoor_2 = pd.DataFrame({"CV_ID":[self.cv_test_2.id],
                              "CV_test_start_t":[cv_test_start_t],
                              "CV_test_end_t":[cv_test_end_t]})
        df_to_add_indoor_2.set_index("CV_ID", inplace=True)
        self.results_df_indoor = pd.concat([self.results_df_indoor, df_to_add_indoor_1, df_to_add_indoor_2])
        #print(self.results_df_indoor)
    
    def generate_master_df(self):
        
        
        self.results_df_rim.to_csv(r"C:\Users\andoi\.spyder-py3\rim_data.csv")
        self.results_df_indoor.to_csv(r"C:\Users\andoi\.spyder-py3\indoor_data.csv")
        
        df_merged_master = pd.merge(self.results_df_rim, self.results_df_indoor, on="CV_ID")
        df_merged_master["CV_rim_q_d"] = df_merged_master["CV_rim_start_t"]- df_merged_master["CV_gen_t"]
        df_merged_master["CV_rim_proc_d"] = df_merged_master["CV_rim_end_t"]- df_merged_master["CV_rim_start_t"]
        df_merged_master["CV_mount_q_d"] = df_merged_master["CV_mount_start_t"]- df_merged_master["CV_rim_end_t"]
        df_merged_master["CV_mount_proc_d"] = df_merged_master["CV_mount_end_t"]- df_merged_master["CV_mount_start_t"]
        df_merged_master["CV_test_q_d"] = df_merged_master["CV_test_start_t"]- df_merged_master["CV_mount_end_t"]
        df_merged_master["CV_test_proc_d"] = df_merged_master["CV_test_end_t"]- df_merged_master["CV_test_start_t"]
        
        self.results_df = df_merged_master
        self.results_df.to_csv(r"C:\Users\andoi\.spyder-py3\run_det.csv")
        
    def calculate_stats(self):
        #self.test_runned = self.results_df["CV_ID"].max()
        self.mean_rim_q_d = self.results_df["CV_rim_q_d"].mean()
        self.mean_rim_proc_d = self.results_df["CV_rim_proc_d"].mean()
        self.mean_mount_q_d = self.results_df["CV_mount_q_d"].mean()
        self.mean_mount_proc_d = self.results_df["CV_mount_proc_d"].mean()
        self.mean_test_q_d = self.results_df["CV_test_q_d"].mean()
        self.mean_test_proc_d = self.results_df["CV_test_proc_d"].mean()
        
    def write_run_results(self):
        with open("trial_results.csv", "a", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            results_to_write = [self.run_number,
                                self.test_runned,
                                self.mean_rim_q_d,
                                self.mean_rim_proc_d,
                                self.mean_mount_q_d,
                                self.mean_mount_proc_d,
                                self.mean_test_q_d,
                                self.mean_test_proc_d]
            writer.writerow(results_to_write)
 
    def run(self):
        
        
        self.env.process(self.generate_cv_st_qced_arrivals())
        self.env.process(self.obstruct_technician())

        self.env.run(until=g.sim_duration)
        
        self.generate_master_df()
        
        self.calculate_stats()
        
        self.write_run_results()
        
class Trial_Results_Calculator:
    def __init__(self):
        self.trial_results_df = pd.DataFrame()
        
    def print_trial_results(self):
        print("TRIAL RESULTS")
        print("-------------")
        
        self.trial_results_df = pd.read_csv("trial_results.csv")
        
        trial_mean_rim_q_d = (self.trial_results_df["Mean_Rim_Q_Duration"].mean())
        trial_mean_rim_proc_d = (self.trial_results_df["Mean_Rim_Proc_Duration"].mean())
        trial_mean_mount_q_d = (self.trial_results_df["Mean_Mount_Q_Duration"].mean())
        trial_mean_mount_proc_d = (self.trial_results_df["Mean_Mount_Proc_Duration"].mean())
        trial_mean_test_q_d = (self.trial_results_df["Mean_Test_Q_Duration"].mean())
        trial_mean_test_proc_d = (self.trial_results_df["Mean_Test_Proc_Duration"].mean())
        
        print ("Mean Queuing Time for Rim over Trial : ",
               round(trial_mean_rim_q_d, 2))
        print ("Mean Processing Time for Rim over Trial : ",
               round(trial_mean_rim_proc_d, 2))
        print ("Mean Queuing Time for Mounting over Trial : ",
               round(trial_mean_mount_q_d, 2))
        print ("Mean Processing Time for Mounting over Trial : ",
               round(trial_mean_mount_proc_d, 2))
        print ("Mean Queuing Time for Testing over Trial : ",
               round(trial_mean_test_q_d, 2))
        print ("Mean Processing Time for Testing over Trial : ",
               round(trial_mean_test_proc_d, 2))

with open("trial_results.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter=",")
    column_headers = ["CV_ID", "# TEST",
                     "Mean_Rim_Q_Duration","Mean_Rim_Proc_Duration",
                     "Mean_Mount_Q_Duration","Mean_Mount_Proc_Duration",
                     "Mean_Test_Q_Duration","Mean_Test_Proc_Duration"]
    writer.writerow(column_headers)
    
for run in range(g.number_of_runs):
    print("Run ", run+1, "of ", g.number_of_runs, sep="")
    my_test_model = lab_model(run)
    my_test_model.run()
    print()

my_trial_results_calculator = Trial_Results_Calculator()
my_trial_results_calculator.print_trial_results()
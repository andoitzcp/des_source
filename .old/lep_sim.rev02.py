# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 22:42:50 2022

@author: andoi
"""

import simpy
import random
import pandas as pd
import csv

# Clase global donde se guardan los parametros de la simulación
class g:
    cv_st_qced_inter = 5
    cv_st_dr_inter = 24*31*2
    cv_st_ece54_inter = 24*31
    cv_st_rr_inter = 24
    cv_st_csa_inter = 48
    
    cv_st_qced_req = 1500
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
    
# Entidad de la simulación, cv=cubierta    
class cv:
    def __init__(self, cv_id, cv_test, cv_client, cv_code):
        self.id = cv_id
        self.test = cv_test
        self.client = cv_client
        self.code = cv_code
        
# Modelo de la simulación
class lab_model:
    
    # Constructor
    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.cv_counter = 0
        self.csqa = 0
        self.rimmed = 0
        
        self.indoor_mach = simpy.Resource(self.env, capacity=g.number_of_indoor_mach)
        self.rr_mach = simpy.Resource(self.env, capacity=g.number_of_rr_mach)
        self.butler_mach = simpy.Resource(self.env, capacity=g.number_of_butler_mach)
        self.technicians = simpy.PreemptiveResource(self.env, capacity=g.number_of_technicians)
        self.operaries = simpy.Resource(self.env, capacity=g.number_of_operaries)
        "self.indoor_rims = simpy.Resources(self.env, capacity=g.number_of_indoor_rims)"
        
        
        self.run_number = run_number
        
        self.test_runned = 0
        self.mean_rim_q_d = 0
        self.mean_rim_proc_d = 0
        self.mean_mount_q_d = 0
        self.mean_mount_proc_d = 0
        self.mean_test_q_d = 0
        self.mean_test_proc_d = 0
        
        self.results_df = pd.DataFrame()
        self.results_df["CV_ID"] = []
        self.results_df["TEST_run"] = []
        self.results_df["CV_gen_t"] = []
        self.results_df["CV_rim_q_d"] = []
        self.results_df["CV_rim_start_t"] = []
        self.results_df["CV_rim_end_t"] = []
        self.results_df["CV_rim_proc_d"] = []
        self.results_df["CV_mount_q_d"] = []
        self.results_df["CV_mount_start_t"] = []
        self.results_df["CV_mount_end_t"] = []
        self.results_df["CV_mount_proc_d"] = []
        self.results_df["CV_test_q_d"] = []
        self.results_df["CV_test_start_t"] = []
        self.results_df["CV_test_end_t"] = []
        self.results_df["CV_test_proc_d"] = []
        self.results_df.set_index("CV_ID", inplace=True)
    
    # Generador de entidades para test QCED del cliente ST    
    def generate_cv_st_qced_arrivals(self):
        while self.csqa<g.cv_st_qced_req:
        
            self.cv_counter += 1
            self.csqa += 1
            
            num_enllantadas = self.csqa
        
            self.csq = cv(self.cv_counter, "QCED", "ST", "CV162")
        
            self.env.process(self.test_proc(self.csq))
        
            sampled_interarrival = random.expovariate(1.0/g.cv_st_qced_inter)
        
            yield self.env.timeout(sampled_interarrival)
            
            print(num_enllantadas)
            
    # Generador de ausencias de los tecnicos fuera de su horario laboral
    def obstruct_technician(self):
        while True:
            yield self.env.timeout(g.shift_duration)
            
            with self.technicians.request(priority=-3, preempt=True) as req_tech_oof:
                
                yield req_tech_oof
                
                yield self.env.timeout(24-g.shift_duration)
                
    # Modelo de los procesos del laboratorio
    def test_proc(self, cubierta):
        
        self.test_runned += 1
        self.test_runned = self.test_runned
        
        cv_gen_t = self.env.now
        
        time_left_rim = random.triangular(12/60, 25/60, 15/60)

        while time_left_rim > 0:    
            
            req_butler = self.butler_mach.request()
            req_tech = self.technicians.request(priority=0, preempt=True)
                        
            yield req_butler & req_tech
        
            cv_rim_start_t = self.env.now
            self.cv_rim_q_d = cv_rim_start_t - cv_gen_t

            try:
        
                yield self.env.timeout(time_left_rim)
                time_left_rim = 0
            except simpy.Interrupt() as interrupt:
                usage = self.env.now - interrupt.cause.usage_since
                time_left_rim -= usage
        
        cv_rim_end_t = self.env.now
        self.cv_rim_proc_d = cv_rim_end_t - cv_rim_start_t
        
        self.butler_mach.release(req_butler)
        self.technicians.release(req_tech)
        
        self.env.process(self.test_proc(self.csq))
        
    def indoor_mach_proc(self, cubierta):
        
        req_indoor = self.indoor_mach.request()
        req_tech = self.technicians.request(priority=-1, preempt=True)
            
        yield req_indoor & req_tech
            
        cv_mount_start_t = self.env.now
        cv_mount_q_d = cv_mount_start_t - self.cv_rim_end_t
            
        sampled_mountage_duration = random.triangular(45/60, 75/60, 180/60)
            
        yield self.env.timeout(sampled_mountage_duration)
            
        cv_mount_end_t = self.env.now
        cv_mount_proc_d = cv_mount_end_t - cv_mount_start_t
            
        self.technicians.release(req_tech)
                        
        yield self.env.timeout(3)
        
        req_tech = self.technicians.request(priority=-2, preempt=False)
            
        yield req_tech
            
        yield self.env.timeout(5/60)
            
        self.technicians.release(req_tech)
        
        cv_test_start_t = self.env.now
        cv_test_q_d = cv_test_start_t - cv_mount_end_t
            
        sampled_test_duration = random.expovariate(1.0/g.mean_test_qced)
                
        yield self.env.timeout(sampled_test_duration)
        
        self.indoor_mach.release(req_indoor)
        
        cv_test_end_t = self.env.now
        cv_test_proc_d = cv_test_end_t - cv_test_start_t
            
        df_to_add = pd.DataFrame({"CV_ID":[cubierta.id],
                                  "TEST_run":[self.test_runned],
                                  "CV_gen_t":[self.cv_gen_t],
                                  "CV_rim_q_d":[self.cv_rim_q_d],
                                  "CV_rim_start_t":[self.cv_rim_start_t],
                                  "CV_rim_end_t":[self.cv_rim_end_t],
                                  "CV_rim_proc_d":[self.cv_rim_proc_d],
                                  "CV_mount_q_d":[cv_mount_q_d],
                                  "CV_mount_start_t":[cv_mount_start_t],
                                  "CV_mount_end_t":[cv_mount_end_t],
                                  "CV_mount_proc_d":[cv_mount_proc_d],
                                  "CV_test_q_d":[cv_test_q_d],
                                  "CV_test_start_t":[cv_test_start_t],
                                  "CV_test_end_t":[cv_test_end_t],
                                  "CV_test_proc_d":[cv_test_proc_d]})
        df_to_add.set_index("CV_ID", inplace=True)
        self.results_df =self.results_df.append(df_to_add)
        self.results_df.to_csv(r"C:\Users\andoi\.spyder-py3\run_det.csv")
    
    # Calculadora de estadisticas de la simulación
    def calculate_stats(self):
        self.test_runned = self.results_df["TEST_run"].max()
        self.mean_rim_q_d = self.results_df["CV_rim_q_d"].mean()
        self.mean_rim_proc_d = self.results_df["CV_rim_proc_d"].mean()
        self.mean_mount_q_d = self.results_df["CV_mount_q_d"].mean()
        self.mean_mount_proc_d = self.results_df["CV_mount_proc_d"].mean()
        self.mean_test_q_d = self.results_df["CV_test_q_d"].mean()
        self.mean_test_proc_d = self.results_df["CV_test_proc_d"].mean()
        
    # Escritor de las estadisticas de la simulación
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
 
    # Controlador de lanzamiento de la simulación
    def run(self):
        self.env.process(self.generate_cv_st_qced_arrivals())
        self.env.process(self.obstruct_technician())

        self.env.run(until=g.sim_duration)
        
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
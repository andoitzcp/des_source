import simpy
import random


class g:
    CV_PR_inter = 24
    mean_test_QCED = 72
    number_of_mach=4
    sim_duration = 24*365
    number_of_runs = 10


class CV_PR:
    def __init__(self, CV_id):
        self.id = CV_id

class Test_QCED_model:
    def __init__(self):
        self.env = simpy.Enviroment()
        self.CV_counter = 0

        self.mach = simpy.Resource(self.env, capacity=g.number_of_mach)

    def generate_CV_PR_arrivals(self):
        while True:
            self.CV_counter += 1

            CPQ = CV_PR(self.CV_counter)

            self.env.process(self.Test_QCED(CPQ))

            sampled_interarrival = random.expovariate(1.0 / g.CV_PR_inter)

            yield self.env.timeout(sampled_interarrival)

    def Test_QCED(self, cubierta):

        print("La cubierta ", cubierta.id, "empezo la espera a las ", self.env.now, sep="")

        with self.mach,request() as req:

            yield req

            print("La cubierta ", cubierta.id, "finaliza la espera a las ", sel.env.now, sep="")

            sampled_test_duration = random.expovariate(1.0 / g.mean_test)

            yield self.env.timeout(sampled_cons_duration)

    def run(self):
        self.env.process(self.generate_CV_PR_arrivals())

        self.env.run(untl=g.sim_durarion)

for run in range(g.number_of_runs):
    print("Run ", run+1, "of ", g.number_of_runs, sep="")
    my_test_model = Test_QCED_model()
    my_test_model.run()
    print()
    

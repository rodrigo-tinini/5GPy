import importlib
import simpy
import functools
import random
import time
from enum import Enum
import numpy
from scipy.stats import norm
import scipy as sp
import scipy.stats
import matplotlib.pyplot as plt
import copy
import simulator as sim
import graph as g

#auxiliar list that keeps the plot markers and colors
markers = ['o', 'v', '^', '<', '>', 's', 'p', 'h', 'H', '+', '<','>']
colors = ['b','g','r','c','m', 'y', 'k', 'r', 'b', 'g', 'r', 'c']

#reset markers and colors
def resetMarkers():
	global markers, colors
	markers = ['o', 'v', '^', '<', '>', 's', 'p', 'h', 'H', '+', '<','>']
	colors = ['b','g','r','c','m', 'y', 'k', 'r', 'b', 'g', 'r', 'c']

#get the blocking probability from the blocked packets and the total generated packets
def calcBlocking(blocked, generated):
	blocking_probability = []
	#iterate over the collection of values in both lists
	for i in range(len(generated)):
		block_list = blocked[i]
		gen_list = generated[i]
		#now, iterate over the lists and calculates the blocking probability
		for j in range(len(gen_list)):
			if gen_list[j] == 0:
				blocking_probability.append(0.0)
			else:
				blocking_probability.append(block_list[j]/gen_list[j])
	return blocking_probability


#Logging
#generate logs
def genLogs(removeHeuristic):
	#iterate over each scheduling policy
	for i in sched_pol:
		#power consumption
		with open('/home/tinini/Área de Trabalho/ons/elsevier/power/power_consumption_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_power_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		#blocked
		with open('/home/tinini/Área de Trabalho/ons/elsevier/blocked/blocked_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_blocking_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
	    #blocking probability
		with open('/home/tinini/Área de Trabalho/ons/elsevier/blocking/blocking_probability_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_blocking_prob_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		#execution times
		with open('/home/tinini/Área de Trabalho/ons/elsevier/exec/exec_times_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_exec_time_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		#average delay
		with open('/home/tinini/Área de Trabalho/ons/elsevier/delay/avg_delay_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_delay_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		#lambda usage
		with open('/home/tinini/Área de Trabalho/ons/elsevier/lambda/lambda_usage_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_lambda_usage_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")

		#confidence interval
		with open('/home/tinini/Área de Trabalho/ons/elsevier/confidence/power_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in power_ci["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/ons/elsevier/confidence/blocking_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in blocking_ci["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/ons/elsevier/confidence/exec_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in exec_ci["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/ons/elsevier/confidence/delay_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in delay_ci["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/ons/elsevier/confidence/lambda_usage_{}_{}_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount, len(g.available_vpons), g.cpri_line),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in lambda_usage_ci["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")

#number of executions
execution_times = 15
#scheduling policies
sched_pol = []
sched_pol.append("cloud_first_all_fogs")
sched_pol.append("fog_first")
sched_pol.append("most_loaded")
sched_pol.append("least_loaded")
#vpon removing policies
remove_pol = []
remove_pol.append("fog_first")
remove_pol.append("cloud_first")
remove_pol.append("random_remove")

#create the lists to keep the results from
average_power = {}
average_blocking = {}
total_reqs = {}
exec_times = {}
blocking_prob = {}
avg_delay = {}
avg_lambda_usage = {}
for i in sched_pol:
	average_power["{}".format(i)] = []
	average_blocking["{}".format(i)] = []
	total_reqs["{}".format(i)] = []
	exec_times["{}".format(i)] = []
	blocking_prob["{}".format(i)] = []
	avg_delay["{}".format(i)] = []
	avg_lambda_usage["{}".format(i)] = []

#resets the lists
def resetLists():
	global average_power, average_blocking, total_reqs, exec_times, avg_delay, avg_lambda_usage
	#create the lists to keep the results from
	average_power = {}
	average_blocking = {}
	total_reqs = {}
	exec_times = {}
	blocking_prob = {}
	avg_delay = {}
	for i in sched_pol:
		average_power["{}".format(i)] = []
		average_blocking["{}".format(i)] = []
		total_reqs["{}".format(i)] = []
		exec_times["{}".format(i)] = []
		blocking_prob["{}".format(i)] = []
		avg_delay["{}".format(i)] = []
		avg_lambda_usage["{}".format(i)] = []

#this function reloads the graph module
def reloadGraphModule():
    importlib.reload(g)

#general function to reload modules
def reloadModule(aModule):
    importlib.reload(aModule)


resetMarkers()
resetLists()

def getBlocking(block, reqs):
	total_blocking = []
	for i in range(len(block)):
		if block[i] == 0:
			total_blocking.append(0)
		else:
			total_blocking.append(block[i]/reqs[i])
	return total_blocking

for i in sched_pol:
	print("Executions of heuristic {}".format(i))
	#begin the experiments
	for j in range(execution_times):
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("Execution #{} of heuristic {}".format(j,i))
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		#simulation environment
		env = simpy.Environment()
		#create the graph
		gp = g.createGraph()
		#create the control plane
		cp = sim.Control_Plane(env, "Graph", gp, i, "fog_first")
		#traffic generator
		tg = sim.Traffic_Generator(env,sim.distribution, None, cp)
		#create the rrhs
		cp.createRRHs(g.rrhs_amount,env)
		random.shuffle(g.rrhs)
		#create fog nodes
		g.addFogNodes(gp, g.fogs)
		#add RRHs to the graph
		g.addRRHs(gp, 0, 64, "0")
		g.addRRHs(gp, 64, 128, "1")
		g.addRRHs(gp, 128, 192, "2")
		g.addRRHs(gp, 192, 256, "3")
		g.addRRHs(gp, 256, 320, "4")
		g.addRRHs(gp, 320, 384, "5")
		g.addRRHs(gp, 384, 448, "6")
		g.addRRHs(gp, 448, 512, "7")
		g.addRRHs(gp, 512, 576, "8")
		g.addRRHs(gp, 576, 640, "9")
		#starts the simulation
		env.run(until = 86401)
		average_power["{}".format(i)].append(sim.average_power_consumption)
		average_blocking["{}".format(i)].append(sim.average_blocking_prob)
		total_reqs["{}".format(i)].append(sim.total_requested)
		exec_times["{}".format(i)].append(sim.average_execution_time)
		avg_lambda_usage["{}".format(i)].append(sim.avg_lambda_usage)
		#print(average_blocking)
		#blocking_prob["{}".format(i)].append(calcBlocking(average_blocking["{}".format(i)], total_reqs["{}".format(i)]))
		blocking_prob["{}".format(i)].append(getBlocking(sim.average_blocking_prob, sim.total_requested))
		#print(blocking_prob)
		avg_delay["{}".format(i)].append(sim.average_delay_time)
		reloadGraphModule()
		reloadModule(sim)

#to calculate the confidence interval
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*numpy.array(data)
    n = len(a)
    m, se = numpy.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    #return m, m-h, m+h
    return h

#calculate the confidence interval
#lists to keep confidence interval
power_ci ={}
blocking_ci ={}
exec_ci = {}
delay_ci = {}
lambda_usage_ci = {}

for i in sched_pol:
	power_ci["{}".format(i)] = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*average_power["{}".format(i)])]
	blocking_ci["{}".format(i)] = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*blocking_prob["{}".format(i)])]
	exec_ci["{}".format(i)] = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*exec_times["{}".format(i)])]
	delay_ci["{}".format(i)] = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*avg_delay["{}".format(i)])]
	lambda_usage_ci["{}".format(i)] = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*avg_lambda_usage["{}".format(i)])]

#calculate the means from the executions
#power consumption means
total_power_mean = {}
for i in sched_pol:
	total_power_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*average_power["{}".format(i)])]

#blocking means
total_blocking_mean = {}
for i in sched_pol:
	total_blocking_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*average_blocking["{}".format(i)])]

#execution times means
total_exec_time_mean = {}
for i in sched_pol:
	total_exec_time_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*exec_times["{}".format(i)])]

#blocking probability means
total_blocking_prob_mean = {}
for i in sched_pol:
	total_blocking_prob_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*blocking_prob["{}".format(i)])]

#average delay means
total_delay_mean = {}
for i in sched_pol:
	total_delay_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*avg_delay["{}".format(i)])]

#average lambda usage means
total_lambda_usage_mean = {}
for i in sched_pol:
	total_lambda_usage_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*avg_lambda_usage["{}".format(i)])]



genLogs("remove_fog_first")





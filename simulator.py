import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
import copy
import sys
import graph as g
import networkx as nx
#keep the lambda usage
lambda_usage = []
avg_lambda_usage = []
#keeps the transmission delays
delay_time = []
average_delay_time = []
#keeps the execution time
execution_time = []
average_execution_time = []
#keeps the blocking probability
blocking_prob = 0
average_blocking_prob = []
#keeps the power consumption
power_consumption = []
average_power_consumption = []
#keeps the average delay on each node
proc_nodes_delay = []
average_proc_nodes_delay = []
#cpri line rate
cpri_line = 614.4
#count the total of requested RRHs
total_requested = []
#count allocated requests
sucs_reqs = 0
total_allocated = []
network_threshold = 0.8
traffic_quocient = 450
#traffic_quocient = 200
#traffic_quocient = 200
#traffic_quocient = 400
rrhs_quantity = 35
served_requests = 0
#timestamp to change the load
change_time = 3600
#the next time
next_time = 3600
#the actual hout time stamp
actual_stamp = 0.0
#inter arrival rate of the users requests
arrival_rate = 3600
#service time of a request
service_time = lambda x: np.uniform(0,100)
#total generated requests per timestamp
total_period_requests = 0
#to generate the traffic load of each timestamp
loads = []
actives = []
#number of timestamps of load changing
stamps = 24
hours_range = range(1, stamps+1)
for i in range(stamps):
	x = norm.pdf(i, 12, 3)
	x *= traffic_quocient
	#x= round(x,4)
	#if x != 0:
	#	loads.append(x)
	loads.append(x)
#distribution for arrival of packets
#first arrival rate of the simulation - to initiate the simulation
arrival_rate = loads[0]/change_time
distribution = lambda x: np.expovariate(arrival_rate)
loads.reverse()
#print(loads)
stamps = len(loads)
#record the requests arrived at each stamp
traffics = []
#amount of rrhs
rrhs_amount = 100
#list of rrhs of the network
rrhs = []

#traffic generator - generates requests considering the distribution
class Traffic_Generator(object):
	def __init__(self, env, distribution, service, cp):
		self.env = env
		self.dist = distribution
		self.service = service
		self.cp = cp
		self.req_count = 0
		self.action = self.env.process(self.run())
		self.load_variation = self.env.process(self.change_load())

	#generation of requests
	def run(self):
		global total_period_requests
		global rrhs
		#global actives
		while True:
			#if rrhs:
			#if total_period_requests <= maximum_load:
			yield self.env.timeout(self.dist(self))
			#total_period_requests +=1
			self.req_count += 1
			#takes the first turned off RRH
			if g.rrhs:
				r = g.rrhs.pop()
				self.cp.requests.put(r)
				#print("Took {}".format(r.id))
				#r.updateGenTime(self.env.now)
				#r.enabled = True
				total_period_requests +=1
				#np.shuffle(rrhs)
			else:
				#print("Empty at {}".format(self.env.now))
				pass


	#changing of load
	def change_load(self):
		while True:
			global traffics
			#global loads
			global arrival_rate
			global total_period_requests
			global next_time
			global power_consumption
			global incremental_power_consumption
			global batch_power_consumption
			global inc_batch_power_consumption
			global incremental_blocking
			global batch_blocking
			global served_requests
			global sucs_reqs
			#self.action = self.action = self.env.process(self.run())
			yield self.env.timeout(change_time)
			actual_stamp = self.env.now
			#print("next time {}".format(next_time))
			next_time = actual_stamp + change_time
			traffics.append(total_period_requests)
			arrival_rate = loads.pop()/change_time
			self.action = self.env.process(self.run())
			self.cp.countAverages()
			#print("traffic: {}".format(len(g.actives_rrhs)*g.cpri_line))
			#print("====================================================================")
			print("Arrival rate now is {} at {} and was generated {}".format(arrival_rate, self.env.now/3600, total_period_requests))
			total_requested.append(total_period_requests)
			total_period_requests = 0
			sucs_reqs = 0

#control plane that controls the allocations and deallocations
class Control_Plane(object):
	def __init__(self, env, type, graph, vpon_scheduling, vpon_remove):
		self.env = env
		self.requests = simpy.Store(self.env)
		self.departs = simpy.Store(self.env)
		self.action = self.env.process(self.run())
		self.deallocation = self.env.process(self.depart_request())
		self.type = type
		self.graph = graph
		self.vpon_scheduling = vpon_scheduling
		self.vpon_remove = vpon_remove
		
	#account the metrics of the simulation
	def countAverages(self):
		global blocking_prob, power_consumption, execution_time, delay_time, lambda_usage
		
		if lambda_usage:
			avg_lambda_usage.append(numpy.mean(lambda_usage))
		else:
			avg_lambda_usage.append(0)
		lambda_usage = []

		if delay_time:
			average_delay_time.append(numpy.mean(delay_time))
		else:
			average_delay_time.append(0)
		delay_time = []

		if blocking_prob != 0:
			average_blocking_prob.append(blocking_prob)
		else:
			average_blocking_prob.append(0)
		blocking_prob = 0
		if power_consumption:
			average_power_consumption.append(numpy.mean(power_consumption))
		else:
			average_power_consumption.append(0)
		power_consumption = []
		if execution_time:
			average_execution_time.append(numpy.mean(execution_time))
		else:
			average_execution_time.append(0)
		execution_time = []

	#create rrhs
	def createRRHs(self, amount, env):
		for i in range(amount):
			#g.rrhs.append(RRH(cpri_line, i, self, self.env))
   			g.rrhs.append(RRH(g.cpri_line, i, self, self.env))
			
	#take requests and tries to allocate on a RRH
	def run(self):
		global blocking_prob

		while True:
			r = yield self.requests.get()
			#print("Got {}".format(r.id))
			#turn the RRH on
			g.startNode(self.graph, r.id)
			g.actives_rrhs.append(r.id)
			g.addActivated(r.id)
			#calls the allocation of VPONs	
			elif self.vpon_scheduling == "fog_first":
				g.fogFirst(self.graph)
			elif self.vpon_scheduling == "cloud_first_all_fogs":
				g.assignVPON(self.graph)
			elif self.vpon_scheduling == "most_loaded":
				g.assignMostLoadedVPON(self.graph)
			elif self.vpon_scheduling == "least_loaded":
				g.assignLeastLoadedVPON(self.graph)
			#execute the max cost min flow heuristic
			start_time = time.clock()
			mincostFlow = g.nx.max_flow_min_cost(self.graph, "s", "d")
			running_time = time.clock() - start_time
			if g.getProcessingNodes(self.graph, mincostFlow, r.id):
				self.env.process(r.run())
				power_consumption.append(g.overallPowerConsumption(self.graph))
				execution_time.append(running_time)
				#lambda_usage.append(g.getLambdaUsage(self.graph))
				total_bd = g.getTotalBandwidth(self.graph)
				#incoming_traffic = len(g.actives_rrhs) * g.cpri_line
				incoming_traffic = g.getTransmittedTraffic(mincostFlow)
				lambda_usage.append(incoming_traffic/total_bd)
				#g.countActNodes(self.graph)
				#print(g.overallDelay(self.graph))
				delay_time.append(g.overallDelay(self.graph))
				#print(len(g.actives_rrhs))
				#g.addActivated(r.id)
				#print("++++++++++++++++++++++++++++++")
				#print(g.fog_activated_rrhs)
				#print(g.activatedFogRRHs())
				#print("++++++++++++++++++++++++++++++")
				#g.getProcessingNodes(self.graph, mincostFlow, r.id)#USAR ESSE METODO PARA VER SE FOI POSSÍVEL COLOCAR O FLUXO DO RRH EM ALGUM NÓ (MODIFICAR A GETpROCESSING PRA RETORNAR O NÓ QUE ELE FOI POSTO)
				#print("Inserted {}".format(r.id))
				#print(mincostFlow[r.id])
			else:
				#print("--------NO FLOW----------- FOR {}".format(len(g.actives_rrhs)))
				#print(len(g.actives_rrhs))
				blocking_prob += 1
				#print("No flow was found!")
				g.minusActivated(r.id)
				g.endNode(self.graph, r.id)
				g.actives_rrhs.remove(r.id)
				g.rrhs.append(r)
				np.shuffle(g.rrhs)
				power_consumption.append(g.overallPowerConsumption(self.graph))

	#starts the deallocation of a request
	def depart_request(self):
		while True:
			r = yield self.departs.get()
			#print("Departing {}".format(r.id))
			g.actives_rrhs.remove(r.id)
			#print("Removing {} from {}".format(r.id, g.rrhs_proc_node[r.id]))
			g.removeRRHNode(r.id)
			g.minusActivated(r.id)
			g.rrhs.append(r)
			g.endNode(self.graph, r.id)
			np.shuffle(g.rrhs)
			#choose the heuristic to remove VPONs
			if self.vpon_remove == "fog_first":
				g.removeVPON(self.graph)
			if self.vpon_remove == "cloud_first":
				g.removeFogFirstVPON(self.graph)
			if self.vpon_remove == "random_remove":
				g.randomRemoveVPONs(self.graph)
			power_consumption.append(g.overallPowerConsumption(self.graph))
			delay_time.append(g.overallDelay(self.graph))
			total_bd = g.getTotalBandwidth(self.graph)
			incoming_traffic = len(g.actives_rrhs) * g.cpri_line
			#print("CALC LAMBDA USAGE FROM DEPART")
			#print("RRHs actives is {}".format(incoming_traffic))
			#print("Total VPONs is {}".format(total_bd))
			if total_bd > 0:
				lambda_usage.append(incoming_traffic/total_bd)
			#lambda_usage.append(g.getLambdaUsage(self.graph))
			#lambda_usage.append((len(g.actives_rrhs)*g.cpri_line)/g.getTotalBandwidth(self.graph))
			#print("Departed Request")
			#print("Cloud is {}".format(g.cloud_vpons))

	#to capture the state of the network at a given rate - will be used to take the metrics at a given (constant) moment
	def checkNetwork(self):
		while True:
			yield self.env.timeout(1800)
			print("Taking network status at {}".format(self.env.now))
			print("Total generated requests is {}".format(total_period_requests))

#rrh
class RRH(object):
	def __init__(self, cpri_line, rrhId, cp, env):
		self.cpri_line = cpri_line
		self.id = "RRH{}".format(rrhId)
		self.cp = cp
		self.env = env

	def run(self):
		#t = np.uniform((next_time -self.env.now)/4, next_time -self.env.now)
		t = np.uniform(900, 3600)
		yield self.env.timeout(t)
		self.cp.departs.put(self)



	#reset the parameters
	def resetParams(self):
		global count, change_time, next_time, actual_stamp, arrival_rate, service_time, total_period_requests, loads, actives, stamps, hours_range, arrival_rate, distribution,traffics
		global power_consumption,average_power_consumption,	batch_power_consumption,batch_average_consumption,incremental_blocking,batch_blocking
		global redirected,activated_nodes,average_act_nodes,b_activated_nodes,b_average_act_nodes
		global activated_lambdas,average_act_lambdas,b_activated_lambdas,b_average_act_lambdas,	activated_dus,average_act_dus,b_activated_dus
		global b_average_act_dus,activated_switchs,	average_act_switch,	b_activated_switchs,b_average_act_switch,redirected_rrhs,average_redir_rrhs
		global b_redirected_rrhs,b_average_redir_rrhs,time_inc,	avg_time_inc,time_b,avg_time_b,count_cloud,	count_fog,b_count_cloud,b_count_fog
		global max_count_cloud,	average_count_fog,b_max_count_cloud,b_average_count_fog,batch_rrhs_wait_time,avg_batch_rrhs_wait_time
		global inc_batch_count_cloud, inc_batch_max_count_cloud, inc_batch_count_fog, inc_batch_average_count_fog, time_inc_batch, avg_time_inc_batch
		global inc_batch_redirected_rrhs, inc_batch_average_redir_rrhs, inc_batch_power_consumption, inc_batch_average_consumption, inc_batch_activated_nodes
		global inc_batch_average_act_nodes, inc_batch_activated_lambdas, inc_batch_average_act_lambdas,	inc_batch_activated_dus, inc_batch_average_act_dus
		global inc_batch_activated_switchs, inc_batch_average_act_switch
		global inc_blocking, total_inc_blocking, batch_blocking, total_batch_blocking, inc_batch_blocking, total_inc_batch_blocking
		global external_migrations, internal_migrations, avg_external_migrations, avg_internal_migrations, served_requests
		global lambda_usage, avg_lambda_usage,proc_usage, avg_proc_usage
		global act_cloud, act_fog, avg_act_cloud, avg_act_fog, daily_migrations
		global count_ext_migrations, total_service_availability, avg_service_availability, avg_total_allocated, total_requested

		total_requested = []
		served_requests = 0
		count = 0
		#timestamp to change the load
		change_time = 3600
		#the next time
		next_time = 3600
		#the actual hout time stamp
		actual_stamp = 0.0
		#inter arrival rate of the users requests
		arrival_rate = 3600
		#service time of a request
		service_time = lambda x: np.uniform(0,100)
		#total generated requests per timestamp
		total_period_requests = 0
		#to generate the traffic load of each timestamp
		loads = []
		actives = []
		#number of timestamps of load changing
		stamps = 24
		hours_range = range(1, stamps+1)
		for i in range(stamps):
			x = norm.pdf(i, 12, 3)
			x *= traffic_quocient
			#x= round(x,4)
			#if x != 0:
			#	loads.append(x)
			loads.append(x)
		#distribution for arrival of packets
		#first arrival rate of the simulation - to initiate the simulation
		arrival_rate = loads[0]/change_time
		distribution = lambda x: np.expovariate(arrival_rate)
		loads.reverse()
		#print(loads)
		stamps = len(loads)
		#record the requests arrived at each stamp
		traffics = []
				#amount of rrhs
		rrhs_amount = 100
		#list of rrhs of the network
		rrhs = []
'''
#starts simulation
#simulation environment
env = simpy.Environment()
#create the graph
gp = g.createGraph()
#create the control plane
cp = Control_Plane(env, "Graph", gp, "small_ratio", "fog_first")
#traffic generator
tg = Traffic_Generator(env,distribution, None, cp)
#create the rrhs
cp.createRRHs(g.rrhs_amount,env)
np.shuffle(g.rrhs)
#create fog nodes
g.addFogNodes(gp, g.fogs)
#add RRHs to the graph
g.addRRHs(gp, 0, 32, "0")
g.addRRHs(gp, 32, 64, "1")
g.addRRHs(gp, 64, 96, "2")
g.addRRHs(gp, 96, 128, "3")
g.addRRHs(gp, 128, 160, "4")
#g.addRRHs(gp, 0, 5, "0")
#g.addRRHs(gp, 5, 10, "1")
#g.addRRHs(gp, 10, 15, "2")
#g.addRRHs(gp, 15, 20, "3")
#g.addRRHs(gp, 20, 25, "4")
#print(g.rrhs_fog)
#starts the simulation
env.run(until = 86401)
'''
#for i in range(len(g.actives_rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
#	print(nx.edges(gp, "RRH{}".format(i)))
#print(nx.edges(gp))
#print(gp["fog0"]["d"]["capacity"])
#neighbors = g.nx.all_neighbors(gp, "s")
#for i in neighbors:
#	print(i)
#print("Cost is {}".format(g.assignVPON(gp)))
#print(g.fog_rrhs)

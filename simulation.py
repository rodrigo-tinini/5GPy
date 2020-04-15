#this is the simulation module, in which the simulation parameters and the simulation itself is initiated
import simpy
import network
import psutil
import utility as util
import networkx as nx
import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm

#simpy environment variable
env = simpy.Environment()
#reads the XML configuration file
parameters = util.xmlParser('configurations.xml')

#initiate input parameters from the entries on the XML file
switchTime = float(parameters["InputParameters"].find("switchTime").text)
frameProcTime = float(parameters["InputParameters"].find("frameProcTime").text)
transmissionTime = float(parameters["InputParameters"].find("transmissionTime").text)
localTransmissionTime = float(parameters["InputParameters"].find("localTransmissionTime").text)
cpriFrameGenerationTime = float(parameters["InputParameters"].find("cpriFrameGenerationTime").text)
distributionAverage = float(parameters["InputParameters"].find("distributionAverage").text)
cpriMode = parameters["InputParameters"].find("cpriMode").text
distribution = lambda x: np.expovariate(1000)
limitAxisY = int(parameters["InputParameters"].find("limitAxisY").text)#limit of axis Y of the network topology on a cartesian plane
limitAxisX = int(parameters["InputParameters"].find("limitAxisX").text)#limit of axis X of the network topology on a cartesian plane
stepAxisY = int(parameters["InputParameters"].find("stepAxisY").text)#increasing step on axis Y when defining the size of the base station
stepAxisX = int(parameters["InputParameters"].find("stepAxisX").text)#increasing step on axis X when defining the size of the base station

#keep the input parameters for visualization or control purposes
inputParameters = []
for p in parameters["InputParameters"]:
	inputParameters.append(p)

#get the attributes of each RRH
rrhsParameters = []
for r in parameters["RRHs"]:
	rrhsParameters.append(r.attrib)

#get the attributes of each node to be created
netNodesParameters = []
for node in parameters["NetworkNodes"]:
	netNodesParameters.append(node.attrib)

#get the attributes of each processing node to be created
procNodesParameters = []
for proc in parameters["ProcessingNodes"]:
	procNodesParameters.append(proc.attrib)

#get the edges for the graph representation
networkEdges = []
for e in parameters["Edges"]:
	networkEdges.append(e.attrib)

#save the id of each element to create the graph
vertex = []
#RRHs
for r in rrhsParameters:
	vertex.append("RRH:"+str(r["aId"]))
#Network nodes
for node in netNodesParameters:
	vertex.append(node["aType"]+":"+str(node["aId"]))
#Processing nodes
for proc in procNodesParameters:
	vertex.append(proc["aType"]+":"+str(node["aId"]))

#create the graph
G = nx.Graph()
#add the nodes to the graph
for u in vertex:
	G.add_node(u)
#add the edges and weights to the graph
for edge in networkEdges:
	G.add_edge(edge["source"], edge["destiny"], weight= float(edge["weight"]))

#create the elements
#create the RRHs
for r in rrhsParameters:
	rrh = network.RRH(env, r["aId"], distribution, cpriFrameGenerationTime, transmissionTime, localTransmissionTime, G, cpriMode)
	network.elements[rrh.aId] = rrh

#create the network nodes
for node in netNodesParameters:
	net_node = network.NetworkNode(env, node["aId"], node["aType"], float(node["capacity"]), node["qos"], switchTime, transmissionTime, G)
	network.elements[net_node.aId] = net_node

#create the processing nodes
for proc in procNodesParameters:
	proc_node = network.ProcessingNode(env, proc["aId"], proc["aType"], float(proc["capacity"]), proc["qos"], frameProcTime, transmissionTime, G)
	network.elements[proc_node.aId] = proc_node

#print(network.elements.keys())

#set the limit area of each base station
util.createNetworkLimits(limitAxisX, limitAxisY, stepAxisX, stepAxisY, network.elements)

#print the coordinate of each base station
util.printBaseStationCoordinates(rrhsParameters, network.elements)


#starts the simulation
print("------------------------------------------------------------SIMULATION STARTED AT {}------------------------------------------------------------".format(env.now))
env.run(until = 3600)
print("------------------------------------------------------------SIMULATION ENDED AT {}------------------------------------------------------------".format(env.now))
print(psutil.virtual_memory())#print the memory consumption for testing
#print("Total of CPRI basic frames: {}".format(network.generatedCPRI))

'''
#Tests
#print the graph
#print([i for i in nx.edges(G)])
print(G.edges())
#print(G["RRH:0"]["Switch:0"]["weight"])
#print(G.graph)
#for i in nx.edges(G):
#	print("{} --> {} Weight: {}".format(i[0], i[1], G[i[0]][i[1]]["weight"]))

#calling Dijkstra to calculate the shortest path. Returning variables "length" and "path" are the total cost of the path and the path itself, respectively
#length, path = nx.single_source_dijkstra(G, "RRH:0", "Cloud:0")
#print(path)

#for i in range(len(rrhs)):
#  print(g["s"]["RRH{}".format(i)]["capacity"])


print("-----------------Input Parameters-------------------")
for i in inputParameters:
	print("{}: {}".format(i.tag, i.text))

print("-----------------RRHs-------------------")
for i in rrhsParameters:
	print(i)

print("-----------------Network Nodes-------------------")
for i in netNodesParameters:
	print(i)

print("-----------------Processing Nodes-------------------")
for i in procNodesParameters:
	print(i)

print("-----------------Edges-------------------")
for i in networkEdges:
	print(i)
'''
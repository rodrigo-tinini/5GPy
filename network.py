import copy
import sys
import abc
import simpy
import functools
import networkx as nx
import random
import time
from enum import Enum
import numpy
import utility as util
from scipy.stats import norm
import psutil


#This is the network module. It keeps all network elements, such as, processing nodes, RRHs, network nodes

#this dictionaire keeps all created network objects
elements = {}
generatedCPRI = 0

#this class represents a general frame
#aId is the fram id, payLoad is its data, src and dst is the source and destiny element, nextHop keeps the path from src to dst, procTime is the average time to process this frame
class Frame(object):
	def __init__(self, aId, payLoad, src, dst):
		self.aId = aId
		self.payLoad = payLoad
		self.src = src
		self.dst = dst
		self.nextHop = []
		self.inversePath = []#return path
		#self.localTransmissionTime = localTransmissionTime
		#self.procTime = procTime
		#self.switchTime = switchTime
		#self.transmissionTime = transmissionTime

#this class extends the basic frame to represent a basic eCPRI frame
#the ideia is that it carries payload from several users equipments and can carry one or more QoS classes of service
#users is a list of UEs being carried, 
#QoS are the classes of service carried on this fram and size is the bit rate of the frame
class ecpriFrame(Frame):
	def __init__(self, aId, payLoad, src, dst, users, QoS, size):
		super().__init__(aId, payLoad, src, dst)
		self.users = users
		self.QoS = QoS
		self.size = size

#this class represents a basic user equipment
#aId is the UE identification, posY and posX are the locations of the UE in a cartesian plane, applicationType is the kind of application accessed by the UE (e.g., video, messaging)
class UserEquipment(object):
	def __init__(self, env, aId, servingRRH, applicationType, localTransmissionTime):
		self.env = env
		self.aId = aId
		self.servingRRH = servingRRH
		#set the beginning position of each UE as the middle of its base station area
		self.posY = self.servingRRH.y2/2 
		self.posX = self.servingRRH.x2/2 
		#self.frameProcTime = frameProcTime
		self.localTransmissionTime = localTransmissionTime
		self.applicationType = applicationType
		self.ackFrames = simpy.Store(self.env)
		self.initiation = self.env.process(self.run())
		#self.action = self.env.process(self.sendFrame())
		self.latency = 0.0
		self.jitter = 0.0
		self.lastLatency = 0.0


	#TODO VOU MUDAR DE NOVO. OS UE NAO VAO GERAR QUADROS, APENAS ANDAR. O RRH AO GERAR O FRAME CPRI ASSUMIRÁ QUE RECEBEU UM QUADRO DE CADA UE
	#O CALCULO DO JITTER E DA TRANSMISSÃO SERÁ FEITO EM CIMA DA POSIÇÃO EM QUE CADA UE SE ENCONTRAR QUANDO O RRH GERAR O FRAME CPRI E QUANDO DEVOLVER (HIPOTETICAMENTE) O QUADRO A CADA UE
	#this method causes UEs to move
	def run(self):
		i = 0
		while True:
			#if i == 0:
				#yield self.env.timeout(self.servingRRH.cpriFrameGenerationTime)
				#self.timeSend[i] = self.env.now
				#newFrame = Frame(i, None, self, None)
				#print("UE {} generating First frame {} to RRH {} at {}".format(hash(self), i, self.servingRRH.aId, self.env.now))
				#yield self.env.timeout(self.localTransmissionTime)
				#self.servingRRH.received_users_frames.put(self)
				#self.servingRRH.received_users_frames.put(newFrame)
			#else:#after generating the first frame, only generate response frames as soon as it get an ACK
				#f = yield self.ackFrames.get()
				#del f
				#update the time when the ACK for frame i was received
				#self.timeReceived[i] = self.env.now
				#yield self.env.timeout(self.localTransmissionTime+self.servingRRH.cpriFrameGenerationTime)#wait for the frame generation windows and transmission time to put it on the RRH
				#print("UE {} sending ACK frame {} to RRH {} at {}".format(hash(self), i, self.servingRRH.aId, self.env.now))
				#self.servingRRH.received_users_frames.put(self)
			#timeout for the UE to move
			yield self.env.timeout(0.5)
			self.randomWalk()
			#print("UE {} moved to position X = {} and Y = {}".format(hash(self), self.posX, self.posY))
			i += 1
	#def run(self):
	#	i = 0
	#	while True:
			#if the UE is recently generated (i = 0), generate the first frame to the RRH
	#		if i == 0:
	#			newFrame = Frame(i, None, self, None)
	#			print("UE {} sending the first frame to RRH {} at {}".format(self.aId, self.servingRRH.aId, self.env.now))
	#			yield self.env.timeout(self.localTransmissionTime)
	#			self.servingRRH.received_users_frames.put(newFrame)
			#timeout for the UE to move
	#		yield self.env.timeout(0.005)
			#print("UE {} moved to position X {} and Y {}".format(self.aId, self.posX, self.posY))
	#		i += 1
	

	#EU PASSEI ISSO PARA A FUNÇÃO ACIMA, POIS O UE GERA UM QUADRO E NO MESMO LOOP ESPERA A RESPOSTA PARA MANDAR OUTRO
	#send frames to its RRH	after it receives an ACK message
	'''
	def sendFrame(self):
		i = 0
		while True:
			f = yield self.ackFrames.get()
			del f
			#print(psutil.virtual_memory())
			#print("UE {} received ack from {} at {}".format(self.aId, self.servingRRH.aId, self.env.now))
			newFrame = Frame(i, None, self, None)
			yield self.env.timeout(self.localTransmissionTime)
			#print("UE {} sending frame {} to RRH {} at {}".format(self.aId, newFrame.aId, self.servingRRH.aId, self.env.now))
			self.servingRRH.received_users_frames.put(newFrame)
			i += 1
	'''
	#TODO: Implement the limits of the UE to move (the combinations of the maximum values of axis y and x)
	#moves the UE
	def randomWalk(self):
		val = random.randint(1, 4)
		if val == 1:
			self.posX += 1
			self.posY = self.posY 
		if val == 2:
			self.posX -= 1
			self.posY = self.posY 
		elif val == 3:
			self.posX = self.posX 
			self.posY += 1
		else:
			self.posX = self.posX 
			self.posY -= 1

#this class represents a generic RRH
#it generates a bunch of UEs, receives/transmits baseband signals from/to them, generate eCPRI frames and send/receive them to/from processing
class RRH(object):
	def __init__(self, env, aId, distribution, cpriFrameGenerationTime, transmissionTime, localTransmissionTime, graph, cpriMode):
		self.env = env
		self.nextNode = None
		self.aType = "RRH"
		self.aId = "RRH"+":"+str(aId)
		self.frames = []
		self.users = []#list of active UEs served by this RRH
		self.nodes_connection = []#binary array that keeps the connection fron this RRH to fog nodes and cloud node(s)
		self.distribution = distribution#the distribution for the traffic generator distribution
		self.trafficGen = self.env.process(self.run())#initiate the built-in traffic generator
		#self.genFrame = self.env.process(self.takeFrameUE())
		self.uplinkTransmitCPRI = self.env.process(self.uplinkTransmitCPRI())#send eCPRI frames to a processing node
		self.downlinkTransmitUE = self.env.process(self.downlinkTransmitUE())#send frames to the UEs
		#thsi store receives frames back from the users
		self.received_users_frames = simpy.Store(self.env)
		#buffer to transmit to UEs
		self.currentLoad = 0
		#this store receives frames back from the processing nodes
		#self.received_eCPRI_frames = simpy.Store(self.env)
		self.processingQueue = simpy.Store(self.env)
		#this store keeps the local processed baseband signals
		self.local_processing_queue = simpy.Store(self.env)
		#self.frameProcTime = frameProcTime
		self.cpriFrameGenerationTime = cpriFrameGenerationTime
		self.transmissionTime = transmissionTime
		self.localTransmissionTime = localTransmissionTime
		self.graph = graph
		self.cpriMode = cpriMode
		#limiting coordinates of the base station area
		self.x1 = 0
		self.x2 = 0
		self.y1 = 0
		self.y2 = 0

	#this method generates users equipments
	def run(self):
		i = 0
		while True:
			yield self.env.timeout(self.distribution(self))
			#a limit for the generation of UEs for testing purposes
			if len(self.users) < 2:
				ue = UserEquipment(self.env, i, self, "Messaging", self.localTransmissionTime)
				self.users.append(ue)
				#print("{} generated UE {} at {}".format(self.aId, hash(ue), self.env.now))
				i += 1

	#every time a frame is received from a UE, keep it to generate the eCPRI frame later
	def takeFrameUE(self):
		while True:
			r = yield self.received_users_frames.get()
			self.frames.append(r)

	#this method builds a eCPRI frame and uplink transmits it to a optical network element
	#ESSE MÉTODO NÃO AGUARDA RECEBER QUADROS DOS USUÁRIOS, MAS QUANDO VAI GERAR O QUADRO CPRI, PEGA A POSIÇÃO DE CADA UE ATIVO PARA PODER CALCULAR A LATENCIA E O JITTER DE CADA UE BASEANDO-SE NA POSIÇÃO DELES
	#EM RELAÇÃO A CARGA DO FRAME eCPRI, A QUANTIDADE DE USUÁRIOS ATIVOS IRÁ INFLUENCIAR. NO CASO DO CPRI NORMAL, INDEPENDENTE DA QUANTIDADE DE UEs ATIVOS, A CARGA DO FRAME VAI SER SEMPRE A MESMA
	#TODO: Update the send time of each UE frame in function of the distance of each UE from the RRH 
	def uplinkTransmitCPRI(self):
		global generatedCPRI
		frame_id = 1
		length, path = nx.single_source_dijkstra(self.graph, self.aId, "Cloud:0")#For now, cloud is the default destiny
		while True:
			yield self.env.timeout(self.cpriFrameGenerationTime)
			print("{} generating eCPRI frame {} at {}".format(self.aId, self.aId+"->"+str(frame_id), self.env.now))
			#print(psutil.virtual_memory())
			#If traditional CPRI is used, create a frame with fixed bandwidth
			activeUsers = []
			if self.cpriMode == "CPRI":
				#take each UE and put it into the CPRI frame
				if self.users:
					for i in self.users:
						activeUsers.append(i)
				#Cloud:0 is the generic destiny for tests purposes - An algorithm will be used to decide in which node it will be placed
				eCPRIFrame = ecpriFrame(self.aId+"->"+str(frame_id), None, self, "Cloud:0", activeUsers, None, None)
				#TODO atualizar o tempo em que cada UE mandou o quadro para o RRH em função da sua distância até ele (ex. env.now - transmissiontTime,  transmissionTime vai ser dinâmico)
				if self.users:
					for i in self.users:
						i.lastLatency = i.latency
						i.latency = (i.latency + self.env.now)/frame_id
				generatedCPRI += 1
			elif self.cpriMode == "eCPRI":
				if self.users:
					for i in self.users:
						activeUsers.append(i)
				frame_size = len(activeUsers)
				eCPRIFrame = ecpriFrame(frame_id, None, self, "Cloud:0", activeUsers, None, frame_size)
				#TODO atualizar o tempo em que cada UE mandou o quadro para o RRH em função da sua distância até ele (ex. env.now - transmissiontTime,  transmissionTime vai ser dinâmico)
				if self.users:
					for i in self.users:
						i.latency = (i.latency + self.env.now)/frame_id
			#calculates the shortest path
			#length, path = nx.single_source_dijkstra(self.graph, self.aId, "Cloud:0")#For now, cloud is the default destiny
			#remove the aId of this node from the path
			eCPRIFrame.nextHop = copy.copy(path)
			eCPRIFrame.inversePath = list(eCPRIFrame.nextHop)
			eCPRIFrame.inversePath.reverse()
			eCPRIFrame.inversePath.pop(0)
			#takes the next hop
			eCPRIFrame.nextHop.pop(0)
			#print("Path for {} is {}".format(self.aId, eCPRIFrame.nextHop))
			#print("Inverse path is {}".format(eCPRIFrame.inversePath))
			destiny = elements[eCPRIFrame.nextHop.pop(0)]
			#print("{} transmitting to {}".format(self.aId, destiny.aId))
			#yield self.env.timeout(self.transmissionTime)
			destiny.processingQueue.put(eCPRIFrame)
			#update the load on the buffer of the destiny node
			destiny.currentLoad += 1
			#print("Frame {} generated".format(eCPRIFrame.aId))
			frame_id += 1
	#This method hipothetically sends an ACK to each UE. The ACK message is modeled as an update on the received time attribute of each UE.
	#The received time is update as a function of the time to send a frame to each UE regarding the distance of each UE from the RRH
	#Note that the calculation of the latency to send the frame in function of the UE position is not yet implemented
	#TODO: Implement the received time for eacj UE in function of its distance to the RRH
	def downlinkTransmitUE(self):
		frame_id = 1
		while True:
			#print(psutil.virtual_memory())
			print("{} transmitting to its UEs".format(self.aId))
			received_frame = yield self.processingQueue.get()
			#yield self.env.timeout(frameProcTime)
			#send an ack to each UE within this received eCPRI frame
			if received_frame.users:
				for i in received_frame.users:
					yield self.env.timeout(self.localTransmissionTime)
					#TODO: atualizar o tempo em que cada UE recebe o quadro de volta em função da sua distância ao RRH (nesse caso, localTransmission time vai ser em função da posição de cada UE)
					#i.timeReceived[i] = self.env.now
					#TODO: Implement the jitter calculation, using the lastLatency variable
					i.jitter = (i.latency + self.env.now)/frame_id
			#update the load on the buffer after processing the frame
			self.currentLoad -= 1
			del received_frame
			#received_frame = None
			frame_id += 1
	
'''	
	#ESSE É O MÉTODO ANTIGO, QUE RECEBIA QUADROS DOS UES.
	#it waits for the time interval for eCPRI frame generation, takes frames previously received and generate the eCPRI frame
	#THIS IS IMPORTANT, IT IS GENERATING CPRI FRAMES EVEN WHEN UEs ARE NOT TRANSMITTING
	#IN OTHER WORDS, THIS IS A CONSTANT BIT RATE TRAFFIC, WHICH IS THE CASE FOR CPRI, NOT ECPRI, FOR eCPRI, CONSIDER UNCOMMENT THE LINE INSIDE THE IF STATEMENT 
	#AND COMMENT THE FRAME GENERATION AFTER THE IF STATEMENT, 
	#FOR TRADITIONAL CPRI, UNCOMMENT ALL FRAMES GENERATION, INSIDE AND OUTSIDE THE IF STATEMENT (IT WILL GENERATE WHATEVER RRHS RECEIVED FRAMES FROM UEs)
	def uplinkTransmitCPRI(self):
		frame_id = 0
		while True:
			yield self.env.timeout(self.cpriFrameGenerationTime)
			print("{} generating eCPRI frame {} at {}".format(self.aId, frame_id, self.env.now))
			activeUsers = []
			if self.frames:
				for i in self.frames:
					activeUsers.append(i)
					#activeUsers.append(i.src)
				#Cloud:0 is the generic destiny for tests purposes - An algorithm will be used to decide in which node it will be placed
				eCPRIFrame = ecpriFrame(frame_id, None, self, "Cloud:0", activeUsers, None, None)
				#generic path for tests purposes
				eCPRIFrame.nextHop = ["Switch:0", "Cloud:0"]#here an algorithm will be invoked to calculate where to send the frame and which path to follow
				#compute the downlink path, which is the same uplink path
			else:
				#Cloud:0 is the generic destiny for tests purposes - An algorithm will be used to decide in which node it will be placed
				eCPRIFrame = ecpriFrame(frame_id, None, self, "Cloud:0", activeUsers, None, None)
				#generic path for tests purposes
				eCPRIFrame.nextHop = ["Switch:0", "Cloud:0"]#here an algorithm will be invoked to calculate where to send the frame and which path to follow
				#compute the downlink path, which is the same uplink path
			frame_id += 1
			#calculates the shortest path
			length, path = nx.single_source_dijkstra(self.graph, self.aId, "Cloud:0")#For now, cloud is the default destiny
			#remove the aId of this node from the path
			eCPRIFrame.nextHop = path
			eCPRIFrame.inversePath = list(eCPRIFrame.nextHop)
			eCPRIFrame.inversePath.reverse()
			eCPRIFrame.inversePath.pop(0)
			#takes the next hop
			eCPRIFrame.nextHop.pop(0)
			#print("Path for {} is {}".format(self.aId, eCPRIFrame.nextHop))
			#print("Inverse path is {}".format(eCPRIFrame.inversePath))
			destiny = elements[eCPRIFrame.nextHop.pop(0)]
			#print("Next hop is ", destiny.aId)
			yield self.env.timeout(self.transmissionTime)
			destiny.processingQueue.put(eCPRIFrame)
			#print("Frame {} generated".format(eCPRIFrame.aId))
'''
	

'''
	#Esse é o método antigo que de fato mandava um quadro para cada UE
	#this method downlink transmits frames to UEs
	def downlinkTransmitUE(self):
		while True:
			print(psutil.virtual_memory())
			#print("{} transmitting to its UEs".format(self.aId))
			#received_frame = yield self.received_eCPRI_frames.get()
			received_frame = yield self.processingQueue.get()
			#send an ack to each UE within this received eCPRI frame
			if self.users:
				for i in received_frame.users:
					yield self.env.timeout(self.localTransmissionTime)
					i.ackFrames.put(received_frame)
'''

#basic network node to be extended
class ActiveNode(metaclass=abc.ABCMeta):
	def __init__(self, env, aId, aType, capacity):
		self.env = env
		self.aType = aType
		self.aId = aType+":"+str(aId)
		self.processingCapacity = capacity
		self.currentLoad = 0
		self.nextNode = None
		self.processingQueue = simpy.Store(self.env)
		self.nextNode = None
		self.lastNode = None
		self.toProcess = self.env.process(self.processRequest())

	#process each frame
	@abc.abstractmethod
	def processRequest(self):
		pass

	#transmit each frame after processing
	@abc.abstractmethod
	def sendRequest(self, request):
		pass

	#test the processing capacity
	def hasCapacity(self):
		if self.currentLoad <= self.processingCapacity:
			return True
		else:
			return False

#a general processing node
class ProcessingNode(ActiveNode):
	def __init__(self, env, aId, aType, capacity, qos, procTime, transmissionTime, graph):
		super().__init__(env, aId, aType, capacity)
		self.qos = qos#list of class of service suppoerted by this node
		self.procTime = procTime
		self.transmissionTime = transmissionTime
		self.graph = graph

	#process a request
	def processRequest(self):
		while True:
			request = yield self.processingQueue.get()
			if self.aId == request.dst:#this is the destiny node. Process it and compute the downlink path
				#rint("Request {} arrived at destination {}".format(request.aId, self.aId))
				#print("This is the path",request.nextHop)
				#print("This is the inverse path", request.inversePath)
				request.nextHop = request.inversePath
			print("{} buffer load is {}".format(self.aId, self.currentLoad))
			print("{} processing request {} at {}".format(self.aId, request.aId, self.env.now))
			yield self.env.timeout(self.procTime)
			#request.direction = "downlink"
			#self.processingCapacity -= 1
			#update the load on the buffer after processing the frame
			self.currentLoad -= 1
			self.sendRequest(request)

	#transmit a request to its destiny	
	def sendRequest(self, request):
		nextHop = request.nextHop.pop(0)#returns the id of the next hop
		destiny = elements[nextHop]#retrieve the next hop object searching by its id
		print("{} sending request {} to {}".format(self.aId, request.aId, destiny.aId))
		print("{} buffer load is {}".format(self.aId, self.currentLoad))
		self.env.timeout(self.transmissionTime)
		destiny.processingQueue.put(request)
		#update the load on the buffer of the destiny node
		destiny.currentLoad += 1
	'''
	def sendRequest(self, request):
		if request.direction == "uplink":
			destiny = self.nextNode
		else:
			destiny = self.lastNode
		#destiny = req.nextHop.pop()
		print("{} sending request {} to {} {}".format(self.aId, request.aId, destiny.aType, destiny.aId))
		self.env.timeout(transmissionTime)
		destiny.processingQueue.put(request)
	'''

#a general processing node
class NetworkNode(ActiveNode):
	def __init__(self, env, aId, aType, capacity, qos, switchTime, transmissionTime, graph):
		super().__init__(env, aId, aType, capacity)
		self.qos = qos#list of class of service suppoerted by this node
		self.switchTime = switchTime
		self.transmissionTime = transmissionTime
		self.graph = graph

	#process a request
	def processRequest(self):
		while True:
			request = yield self.processingQueue.get()
			print("{} buffer load is {}".format(self.aId, self.currentLoad))
			#print("Request {} arrived at {}".format(request.aId, self.aId))
			print("{} processing request {} at {}".format(self.aId, request.aId, self.env.now))
			#yield self.env.timeout(self.switchTime)
			#update the load on the buffer after processing the frame
			self.currentLoad -= 1
			#self.processingCapacity -= 1
			self.sendRequest(request)

	#transmit a request to its destiny
	def sendRequest(self, request):
		nextHop = request.nextHop.pop(0)#returns the id of the next hop
		destiny = elements[nextHop]#retrieve the next hop object searching by its id
		print("{} sending request {} to {}".format(self.aId, request.aId, destiny.aId))
		#self.env.timeout(self.transmissionTime)
		destiny.processingQueue.put(request)
		#update the load on the buffer of the destiny node
		destiny.currentLoad += 1
	'''
	def sendRequest(self, request):
		if request.direction == "uplink":
			destiny = self.nextNode
		else:
			destiny = self.lastNode
		#destiny = req.nextHop.pop()
		print("{} sending request {} to {} {}".format(self.aId, request.aId, destiny.aType, destiny.aId))
		self.env.timeout(transmissionTime)
		destiny.processingQueue.put(request)
	'''

#this class represents the control plane that will be responsible to invoke algorithms to place vBBUs and to assign wavelengths
#it will keep the representations of the topology that will be used by the algorithms, e.g., graph or ILP
#in the case of the ILP, it is necessary that every object created is represented as binary arrays for the ILP to solve it, as we did before
class ControlPlane(object):
	pass
'''
def sendRequest(self, request):
	print("{} sending request {} to {} {}".format(self.aId, request.aId, destiny.aType, destiny.aId))
	nextHop = request.nextHop.pop()
	destiny = nextHop
	destiny.processingQueue.put(request)
	self.env.timeout(transmissionTime)
	destiny.processingQueue.put(request)
'''

'''
#tests
elements = {}#to keep reference to each network element
switchTime = 0.0001
frameProcTime = 0.0001
transmissionTime = 0.0000001
cpriFrameGenerationTime = 0.5
distribution = lambda x: np.expovariate(1000)
env = simpy.Environment()
rrh = RRH(env, 0, distribution)
elements[rrh.aId] = rrh
network_node = NetworkNode(env, 0, "Switch", 100, None)
elements[network_node.aId] = network_node
processing_node = ProcessingNode(env, 0, "Cloud", 100, None)
elements[processing_node.aId] = processing_node
print(elements)
rrh.nextNode = network_node
print("------------------------------------------------------------SIMULATION STARTED AT {}------------------------------------------------------------".format(env.now))
env.run(until = 10)
print("------------------------------------------------------------SIMULATION ENDED AT {}------------------------------------------------------------".format(env.now))
#TODO: Implementar a questão do caminho a ser seguido por cada quadro eCPRI a partir do momento que é gerado no RRH
#para testar, eu estou considerando apenas um caminho simples de ida e um de volta para testar a comunicação entre os elementos
'''
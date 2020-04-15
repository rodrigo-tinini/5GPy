#this is the utility module, where every utility method must be put, including methods that calculates metrics from the simulation
import xml.etree.ElementTree as ET
import networkx as nx

#XML parser
def xmlParser(xmlFile):
	#keep the configuration parameters
	parameters = {}
	#construct the XML tree
	tree = ET.parse(xmlFile)
	#get the root
	root = tree.getroot()
	#return root
	##iterate over the nodes and  store each one into the parameters dictionaire
	for child in root:
		parameters[child.tag] = child
	return parameters

#call Dijkstra shortest path algorithm
def dijkstraShortestpath(G, source, destiny):
	length, path = nx.single_source_dijkstra(G, source, destiny)
	return length, path

#create the limits of each base station/RRH following a cartesian plane
def createNetworkLimits(limitX, limitY, stepX, stepY, elements):
	#dictionaire to keep all coordinates of a base station
	#coordinates = {}
	#to place each base station in a dictionaire position
	i = 0
	#until the limit of axis x, go upside until the limite of axis y
	x = 0
	while x < limitX:
		#print("X equal to {}".format(x))
		y = 0
		while y < limitY:
			#coordinates["RRH:{}".format(i)] = [(x, y), (x, y+1), (x+1, y), (x+1, y+1)]#old implementation
			elements["RRH:{}".format(i)].x1 = x
			elements["RRH:{}".format(i)].y1 = y
			elements["RRH:{}".format(i)].x2 = x + 1
			elements["RRH:{}".format(i)].y2 = y + 1
			#print("Coordinates: x1 y1 {}, x1 y 2 {}, x2 y1 {}, x2 y2 {}".format((x, y), (x, y+1), (x+1, y), (x+1, y+1)))
			y += stepY
			#y += 1
			i += 1
		x += stepX
		#x += 1
	#print the coordinate of each RRH
	#for key, value in coordinates.items():
	#	print(key, " :", value)

#test
#createNetworkLimits(5, 4)

#print the coordinates of each base station
def printBaseStationCoordinates(baseStations, elements):
	for r in baseStations:
		print("{} coordinates are: \n X1: {}\n Y1: {}\n X2: {}\n Y2: {}\n".format(elements["RRH:{}".format(r["aId"])].aId,
			elements["RRH:{}".format(r["aId"])].x1, elements["RRH:{}".format(r["aId"])].y1, elements["RRH:{}".format(r["aId"])].x2, elements["RRH:{}".format(r["aId"])].y2))


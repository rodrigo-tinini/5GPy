import xml.etree.ElementTree as ET
import networkx as nx

def xmlParser(xmlFile):

	parameters = {}
	tree = ET.parse(xmlFile)
	root = tree.getroot()

	##iterate over the nodes and  store each one into the parameters dictionaire
	for child in root:
		parameters[child.tag] = child
	return parameters

def dijkstraShortestpath(G, source, destiny):

	length, path = nx.single_source_dijkstra(G, source, destiny)
	return length, path

def createNetworkLimits(limitX, limitY, stepX, stepY, elements):

	#dictionaire to keep all coordinates of a base station
	#coordinates = {}
	#to place each base station in a dictionaire position
	i = 0
	#until the limit of axis x, go upside until the limite of axis y
	x = 0
	while x < limitX:
		y = 0
		while y < limitY:
			#coordinates["RRH:{}".format(i)] = [(x, y), (x, y+1), (x+1, y), (x+1, y+1)]#old implementation
			elements["RRH:{}".format(i)].x1 = x
			elements["RRH:{}".format(i)].y1 = y
			elements["RRH:{}".format(i)].x2 = x + 1
			elements["RRH:{}".format(i)].y2 = y + 1
			y += stepY
			i += 1
		x += stepX

def printBaseStationCoordinates(baseStations, elements):

	for r in baseStations:
		print("{} coordinates are: \n X1: {}\n Y1: {}\n X2: {}\n Y2: {}\n".format(elements["RRH:{}".format(r["aId"])].aId,
			elements["RRH:{}".format(r["aId"])].x1, elements["RRH:{}".format(r["aId"])].y1, elements["RRH:{}".format(r["aId"])].x2, elements["RRH:{}".format(r["aId"])].y2))


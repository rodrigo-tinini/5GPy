from random import randint, uniform, random

import networkx as nx
import numpy as np

TOTAL_RRHS = 4
TOTAL_NETWORK_NODES = 4
TOTAL_PROCESSING_NODES = 1
DEFAULT_RRH_INFO = {}
DEFAULT_NETWORK_NODE_INFO = {"aType": "Switch", "capacity": "10000", "qos": "Standard"}
DEFAULT_PROCESSING_NODE_INFO = {"aType": "Cloud", "capacity": "10000", "qos": "Standard"}

def create_network(total_rrhs = TOTAL_RRHS,
                    rrh_info = DEFAULT_RRH_INFO,
                    total_network_nodes = TOTAL_NETWORK_NODES,
                    network_node_info = DEFAULT_NETWORK_NODE_INFO,
                    total_processing_nodes = TOTAL_PROCESSING_NODES,
                    processing_node_info = DEFAULT_PROCESSING_NODE_INFO):

    print("Creating newtork.............")
    network_graph = nx.Graph()

    network_graph = add_nodes(network_graph, total_rrhs, rrh_info, "RRH")
    network_graph = add_nodes(network_graph, total_network_nodes, network_node_info, "Switch")
    network_graph = add_nodes(network_graph, total_processing_nodes, processing_node_info, "Cloud")

    network_graph = add_random_edges(network_graph)

    print("Done")
    return network_graph

# for now, this is only adding the same parameters for
# every node_type.
def add_nodes(network_graph, node_qty, node_info, node_type):

    for i in range(node_qty):
        node_info["aId"] = i
        node_id = f"{node_type}:{node_info['aId']}"
        network_graph.add_node(node_id)

        for attr in node_info:
            network_graph.nodes[node_id][f"{attr}"] = node_info[attr]

    return network_graph


def add_random_edges(network_graph):

    rrhs = [i for i in network_graph.nodes() if "RRH" in i]
    switches = [i for i in network_graph.nodes() if "Switch" in i]
    clouds = [i for i in network_graph.nodes() if "Cloud" in i]

    # each rrh must be connected to a switch node
    for idx, rrh in enumerate(rrhs):
        # pseudo-random switch
        # switch_idx = len(switches)*idx % len(switches)
        switch_idx = (idx + 3) % len(switches)
        weight = np.round(uniform(1,5),1)
        network_graph.add_edge(rrh, switches[switch_idx], weight = weight)

    # switch nodes can or cannot be connected between each other
    for idx, switch in enumerate(switches):
        switch_idx = (idx + 3) % len(switches)
        weight = np.round(uniform(1,5),1)
        network_graph.add_edge(switch, switches[switch_idx], weight = weight)

    # at least one switch has to be connected to the cloud
    rand_switch = randint(0,len(switches)-1)
    network_graph.add_edge(switches[rand_switch], clouds[0], weight = weight)

    validate_graph(network_graph)

    return network_graph

def add_edges(network_graph, src_nodes, dst_nodes, weights):

    for src, dst, w in zip(src_nodes, dst_nodes, weights):
        network_graph.add_edge(src, dst, weight = w)

    validate_graph(network_graph)
    return network_graph

def validate_graph(network_graph):

    rrhs = [i for i in network_graph.nodes() if "RRH" in i]
    switches = [i for i in network_graph.nodes() if "Switch" in i]
    clouds = [i for i in network_graph.nodes() if "Cloud" in i]

    for i in rrhs:
        if nx.has_path(network_graph, i, clouds[0]) == False:
            raise ValueError("there is one RRHs which is not connected to the cloud. please check your graph")

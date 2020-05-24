import sys
import random
import xml.etree.ElementTree as ET

import numpy as np

import graph

def indent(elem, level=0):

    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def create_base_file(switch_time=0.0001, frame_proc_time=0.0001,
        transmission_time=0.0000001, local_transmission_time=0.0000001,
        cpri_frame_generation_time=0.001, distribution_average=1000,
        cpri_mode='CPRI', limit_axis_y=2, limit_axis_x=2, step_axis_y=1,
        step_axis_x=1):

    config = ET.Element('config')

    input_parameters = ET.SubElement(config, 'InputParameters')
    st = ET.SubElement(input_parameters, 'switchTime')
    st.text = f"{switch_time}"

    fcp = ET.SubElement(input_parameters, 'frameProcTime')
    fcp.text = f"{frame_proc_time}"

    tt = ET.SubElement(input_parameters, 'transmissionTime')
    tt.text = f"{transmission_time}"

    lt = ET.SubElement(input_parameters, 'localTransmissionTime')
    lt.text = f"{local_transmission_time}"

    cfgt = ET.SubElement(input_parameters, 'cpriFrameGenerationTime')
    cfgt.text = f"{cpri_frame_generation_time}"

    da = ET.SubElement(input_parameters, 'distributionAverage')
    da.text = f"{distribution_average}"

    cm = ET.SubElement(input_parameters, 'cpriMode')
    cm.text = cpri_mode

    lay = ET.SubElement(input_parameters, 'limitAxisY')
    lay.text = f"{limit_axis_y}"

    lax = ET.SubElement(input_parameters, 'limitAxisX')
    lax.text = f"{limit_axis_x}"

    say = ET.SubElement(input_parameters, 'stepAxisY')
    say.text = f"{step_axis_y}"

    sax = ET.SubElement(input_parameters, 'stepAxisX')
    sax.text = f"{step_axis_x}"

    network_graph = graph.create_network()
    rrh_nodes =  [i for i in network_graph.nodes if "RRH" in i]
    switch_nodes =  [i for i in network_graph.nodes if "Switch" in i]
    cloud_nodes =  [i for i in network_graph.nodes if "Cloud" in i]

    rrhs = ET.SubElement(config, 'RRHs')

    for rrh in rrh_nodes:
        element = ET.SubElement(rrhs, 'RRH')

        for attr in network_graph.nodes[rrh]:
            element.set(attr, str(network_graph.nodes[rrh][attr]))


    # TODO: find out what different values aTypes field can have so it wont be
    # hardcoded like the ones below
    switches = ET.SubElement(config, 'NetworkNodes')
    for switch in switch_nodes:
        element = ET.SubElement(switches, 'Node')
        for attr in network_graph.nodes[switch]:
            element.set(attr, str(network_graph.nodes[switch][attr]))


    clouds = ET.SubElement(config, 'ProcessingNodes')
    for cloud in cloud_nodes:
        element = ET.SubElement(clouds, 'Node')

        for attr in network_graph.nodes[cloud]:
            element.set(attr, str(network_graph.nodes[cloud][attr]))


    edges = network_graph.edges.data()

    es = ET.SubElement(config, 'Edges')
    for edge in edges:
        element = ET.SubElement(es, 'Edge')

        # `e` is a tuple like (src, dst, {weight: x})
        element.set('source', edge[0])
        element.set('destiny', edge[1])
        element.set('weight', str(edge[2]['weight']))

    return config


if __name__ == '__main__':
    config = create_base_file()
    tree = ET.ElementTree(config)
    root = tree.getroot()

    indent(root)

    tree.write(sys.argv[1])

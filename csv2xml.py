import sys
import random
import xml.etree.ElementTree as ET

#import pandas as pd
import numpy as np

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

    # setup random rrhs
    rrhs = ET.SubElement(config, 'RRHs')
    n_rrh = random.randint(2,5)
    for rrh in range(n_rrh):
        aId = ET.SubElement(rrhs, 'RRH')
        aId.set('aId', f"{rrh}")


    # set random network nodes
    # TODO: find out what different values aTypes field can have so it wont be
    # hardcoded like the ones below
    nns = ET.SubElement(config, 'NetworkNodes')
    n_nns = random.randint(2,5)
    for nn in range(n_nns):
        aId = ET.SubElement(nns, 'Node')
        aId.set('aId', f"{nn}")
        aId.set('aType', 'Switch')
        aId.set('capacity', '10000')
        aId.set('qos', 'Standard')


    pns = ET.SubElement(config, 'ProcessingNodes')
    n_pns = random.randint(2,5)
    for pn in range(n_pns):
        aId = ET.SubElement(pns, 'Node')
        aId.set('aId', f"{pn}")
        aId.set('aType', 'Cloud')
        aId.set('capacity', '10000')
        aId.set('qos', 'Standard')


    es = ET.SubElement(config, 'Edges')
    # each rrh must be connected to at least one switch?
    # switchs could be interconnected, forming a graph
    # at least one switch should be connected to the cloud
    for i in range(n_rrh):
        edge = ET.SubElement(es, 'Edge')
        edge.set('source', f"RRH:{i}")
        edge.set('destiny', f"Switch:{random.randint(1,n_nns)}")
        edge.set('weight', f"{np.round(random.uniform(0, 5),2)}")

    for i in range(n_nns):
        edge = ET.SubElement(es, 'Edge')
        edge.set('source', f"Switch:{i}")
        edge.set('destiny', f"Switch:{random.randint(1,n_nns)}")
        edge.set('weight', f"{np.round(random.uniform(0, 5), 2)}")

    # FIXME: here, the switch should have an available path so it can
    # connect to the cloud
    edge = ET.SubElement(es, 'Edge')
    edge.set('source',f"Switch:{np.round(random.randint(1,n_nns),2)}")
    edge.set('destiny', 'Cloud:0')
    edge.set('weight', f"{random.uniform(0, 5)}")

    return config


if __name__ == '__main__':
    config = create_base_file()
    tree = ET.ElementTree(config)
    root = tree.getroot()

    indent(root)

    tree.write(sys.argv[1])

import json
import os
from typing import List
from src.models.node import Node
from src.models.edge import Edge

def load_flow_from_json(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Flow definition file not found: {file_path}")
    
    with open(file_path,'r') as f:
        flow_data = json.load(f)
    
    nodes = {}

    for node_data in flow_data:
        node_id = node_data.get('nodeId')
        prompt = node_data.get('prompt')
        root_node = node_data.get('rootNode', False)

        node = Node(node_id,prompt, root_node=root_node)
        nodes[node_id] = node
    
    for node_data in flow_data:
        node_id = node_data.get('nodeId')
        edges_data = node_data.get('edges',[])

        for edges_data in edges_data:
            condition = edges_data.get('condition')
            targetNode_id = edges_data.get('targetNodeId')

            edge = Edge(condition, targetNode_id=targetNode_id)
            nodes[node_id].add_edge(edge)
    
    return nodes

def get_root_node(nodes):
    for node in nodes.values():
        if node.root_node:
            return node
    
    if nodes:
        return List(nodes.values())[0]
    
    raise ValueError("No nodes found in the flow")
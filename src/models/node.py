class Node:
    def __init__(self, node_id, prompt, root_node=None, edges=None):
        self.node_id = node_id
        self.prompt = prompt
        self.edges = edges or []
        self.root_node = root_node

    def add_edge(self, edge):
        self.edges.append(edge)
        
    def __str__(self):
        return f"Node({self.node_id}), edges: {len(self.edges)}"
class Edge:
    def __init__(self,condition, target_node_id):
        self.condition = condition
        self.target_node_id = target_node_id
    def __str__(self):
        return f"Edge({self.condition} -> {self.target_node_id})"
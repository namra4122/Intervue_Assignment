class Edge:
    def __init__(self,condition, targetNode_id):
        self.conition = condition
        self.targetNode_id = targetNode_id
    
    def __str__(self):
        return f"Edge({self.conition} -> {self.targetNode_id})"
    
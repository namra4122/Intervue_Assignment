from time import timezone
import uuid
from typing import List, TypedDict, Callable, Dict, Any
from datetime import datetime, timezone
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

class FlowService:
    def __init__(self, nodes, llm_service):
        print("debug_logs = IN FlowService.__init__")
        self.nodes = nodes
        self.llm_service = llm_service
        self.current_node = None
        self.chat_history = []

        for node in nodes.values():
            if node.root_node:
                self.current_node = node
                break
        
        if not self.current_node and nodes:
            self.current_node = list(nodes.values())[0]
        
        print(f"--------------------{self.current_node}--------------------")
        
        self._setup_langgraph()
    
    def _setup_langgraph(self):
        print("debug_logs = IN FlowService._setup_langgraph")
        self.memory = MemorySaver()

        class Input_schema(TypedDict):
            message: str
            history: List[Dict[str, str]]

        class Output_schema(TypedDict):
            response: str

        self.graph = StateGraph(input=Input_schema, output=Output_schema)

        self.graph.add_node("process_message", self._process_node)
        self.graph.add_edge(START, "process_message")
        self.graph.add_edge("process_message", END)

        self.workflow = self.graph.compile(
            checkpointer=self.memory,
        )
    
    def _process_node(self, state):
        print("debug_logs = IN FlowService._process_node")
        msg = state.get("message", "")
        history = state.get("history", "")
        print(f"--------------------{history}--------------------")
        self.chat_history = history

        if self.chat_history and msg:
            self._process_user_input(msg)

        response = self.llm_service.generate_response(self.current_node.prompt, self.chat_history)

        return {
            "response" : response,
            "current_node" : self.current_node.node_id,
            "history" : self.chat_history + [
                {"role" : "user", "content" : msg},
                {"role": "assistant", "content" : response}
            ]
        }

    def process_user_input(self, user_input, username, q_count):
        print("debug_logs = IN FlowService.process_user_input")
        state = {
            "message": user_input,
            "history": self.chat_history
        }
        thread_id = uuid.uuid4()
        result = self.workflow.invoke(
            state,
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "thread_ts": datetime.now(timezone.utc).isoformat(),
                    "checkpoint_id": f"session-{thread_id}-q{q_count}",
                    "checkpoint_ns": f"interview-{username}"
                }
            }
        )

        self.chat_history = result["history"]

        return result["response"]

    def _process_user_input(self, user_input):
        print("debug_logs = IN FlowService._process_user_input")
        if not self.current_node:
            return

        if not self.current_node.edges:
            return
        
        conditions = [edge.condition for edge in self.current_node.edges]

        matching_condition = self.llm_service.evaluate_condition(
            user_input, conditions, self.chat_history
        )

        for edge in self.current_node.edges:
            if edge.condition ==  matching_condition:
                self.current_node = self.nodes.get(edge.target_node_id)
                break
    
    def reset(self):
        for node in self.nodes.values():
            if node.root_node:
                self.current_node = node
                break
        
        self.chat_history = []
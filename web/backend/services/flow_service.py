import uuid
from typing import List, TypedDict, Dict
from datetime import datetime, timezone
from google.genai import types
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from services.llm_service import LLMService

class FlowService:
    def __init__(self, nodes, llm_service: LLMService):
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
        
        self._setup_langgraph()
    
    def _setup_langgraph(self):
        self.memory = MemorySaver()

        class Input_schema(TypedDict):
            message: str
            history: List[Dict[str, str]]

        class Output_schema(TypedDict):
            response: str
            history: List[Dict[str, str]]

        self.graph = StateGraph(input=Input_schema, output=Output_schema)

        self.graph.add_node("process_message", self._process_node)
        self.graph.add_edge(START, "process_message")
        self.graph.add_edge("process_message", END)

        self.workflow = self.graph.compile(
            checkpointer=self.memory,
        )
    
    def _process_node(self, state):
        message = state.get("message", "")
        history = state.get("history", [])
        self.chat_history.extend(history)

        if self.chat_history and message:
            self._process_user_input(message)
        
        response_chunk = self.llm_service.generate_response(self.current_node.prompt, self.chat_history)
        response = ""
        for chunk in response_chunk:
            response = response + chunk.text if chunk.text else ""
        
        return {
            "response": response,
            "current_node": self.current_node.node_id,
            "history": self.chat_history + [
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response)]
                )
            ]
        }
    
    def process_user_input(self, user_input, username, q_count):
        self.chat_history.append(
            types.Content(
                role="user", parts=[types.Part.from_text(text=user_input)]
            )
        )
        
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

        if "history" in result:
            self.chat_history = result["history"]
        
        response = result.get("response", "I'm not sure how to respond to that.")
        
        if "current_node" in result:
            node_id = result.get("current_node")
            if node_id in self.nodes:
                self.current_node = self.nodes[node_id]
        
        return response

    def _process_user_input(self, user_input):
        if not self.current_node or not self.current_node.edges:
            return False
        
        conditions = [edge.condition for edge in self.current_node.edges]

        matching_condition = self.llm_service.eval_condition(
            user_input, conditions, self.chat_history
        )

        transitioned = False
        for edge in self.current_node.edges:
            if edge.condition ==  matching_condition:
                self.current_node = self.nodes.get(edge.target_node_id)
                transitioned = True
                break
        
        return transitioned
    
    def reset(self):
        self.current_node = None
        self.chat_history = []
        for node in self.nodes.values():
            if node.root_node:
                self.current_node = node
                break
        
        if not self.current_node and self.nodes:
            self.current_node = list(self.nodes.values())[0]
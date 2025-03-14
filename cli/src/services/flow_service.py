import uuid
from typing import List, TypedDict, Dict
from datetime import datetime, timezone
from google.genai import types
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

class FlowService:
    def __init__(self, nodes, llm_service):
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
        msg = state.get("message", "")
        history = state.get("history", [])
        self.chat_history = history

        if self.chat_history and msg:
            self._process_user_input(msg)
        

        response_chunk = self.llm_service.generate_response(self.current_node.prompt, self.chat_history)
        response = ""
        for chunk in response_chunk:
            response += chunk.text if chunk.text else ""

        return {
            "response" : response,
            "current_node" : self.current_node.node_id,
            "history" : self.chat_history + [
                types.Content( role="model", parts=[ types.Part.from_text(text=response),],),
            ]
        }

    def process_user_input(self, user_input, username, q_count):
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

        # # Check if history exists in the result, otherwise keep the existing history
        # if "history" in result:
        #     self.chat_history = result["history"]

        #update chat history with model response if available
        response = result.get("response","I'm not sure how to respond to that.")
        if response and not any (
            content.role == "model" and content.parts[0].text == response for content in self.chat_history if content.role == "model"
        ):
            self.chat_history.append(
                types.Content(
                    role="model",
                    parts = [types.Part.from_text(text=response)]
                )
            )
        
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

        # debug_print
        print(f"Matching condition: {matching_condition}")

        transitioned = False
        for edge in self.current_node.edges:
            if edge.condition ==  matching_condition:
                self.current_node = self.nodes.get(edge.target_node_id)
                transitioned = True
                self.chat_history.append(
                    types.Content(
                        role="user", parts=[types.Part.from_text(text=user_input)]
                    )
                )
                # debug_print
                print(f"Transitioned to node: {self.current_node.node_id}")
                break
        
        return transitioned

    def reset(self):
        for node in self.nodes.values():
            if node.root_node:
                self.current_node = node
                break
        
        self.chat_history = []
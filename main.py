import os
import sys
from dotenv import load_dotenv
from google.genai import types
from src.utils.json_loader import load_flow_from_json
from src.services.llm_service import LLMService
from src.services.flow_service import FlowService

load_dotenv()

def main(username = None):
    basedir = os.path.dirname(os.path.abspath(__file__))
    flow_dir = os.path.join(basedir, 'config', 'interview_flow.json' )

    if username is None:
        username = input("Please enter the expected candidate's username: ")
    
    try:
        nodes = load_flow_from_json(flow_dir)
        print(f"Loaded {len(nodes)} nodes from flow definition")
    except Exception as e:
        print(f"Error loading flow: {e}")
        return
    
    llm_service = LLMService(username)
    flow_service = FlowService(nodes, llm_service)

    print(f"Flow-Based Interview Chatbot (Expected candidate: {username})")
    print("Type 'exit' to quit")

    if flow_service.current_node:
        initial_response = llm_service.generate_response(flow_service.current_node.prompt)
        flow_service.chat_history.append(
            types.Content( role="model", parts=[ types.Part.from_text(text=initial_response),],)
        )
        print(f"Chatbot: {initial_response}")
    
    question_count = 0
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("GoodBye !!")
            break
        question_count = question_count + 1
        response = flow_service.process_user_input(user_input=user_input, username=username, q_count=question_count)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
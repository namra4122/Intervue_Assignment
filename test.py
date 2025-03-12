import os
from dotenv import load_dotenv
# import google.genai as genai
# from google.genai.types import Content, Part, GenerateContentConfig

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# class LLMService:
#     def __init__(self, expected_username):
#         self.client = genai.Client(
#             api_key=GEMINI_API_KEY
#         )
#         self.model = 'gemini-2.0-flash'
#         self.username = expected_username
    
#     def generate_response(self, prompt, chat_history=None):
#         user_prompt = prompt.replace("{username}", self.username)

#         try:
#             if chat_history:
#                 generate_content_config = GenerateContentConfig(
#                     temperature=1,
#                     top_p=0.95,
#                     top_k=40,
#                     max_output_tokens=8192,
#                     response_mime_type="text/plain",
#                 )

#                 res = self.client.models.generate_content_stream(
#                     model = self.model,
#                     contents=chat_history + [
#                         Content(
#                             role="model", 
#                             parts=[Part.from_text(text=user_prompt)]
#                         )
#                     ],
#                     config=generate_content_config,
#                 )

#                 for chunk in res:
#                     print(chunk.text)
            
#         except Exception as e:
#             print(f"Error generating response: {e}")
#             return f"I'm having trouble processing that request: {str(e)}"

# # Example usage with proper chat history format
# if __name__ == "__main__":
#     # Example of properly formatted chat history
#     chat_history = [
#         Content(
#             role="model",
#             parts=[Part.from_text(text = "Are you Namra")]
#         ),
#         Content(
#             role="user",
#             parts=[Part.from_text(text = "yes i am")]
#         ),
#     ]
    
#     service = LLMService("Namra")
#     service.generate_response("Introduce yourself & ask if we can conduct interview with {username} right now", chat_history)


from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    api_key=GEMINI_API_KEY,
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

messages = [
    (
        "human",
        "ask if you are namra?",
    ),
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)
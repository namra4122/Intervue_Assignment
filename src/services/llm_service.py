import google.generativeai as agi
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

class LLMService:
    def __init__(self, expected_username):
        print("debug_logs = IN LLMService.__init__")
        agi.configure(api_key=GEMINI_API_KEY)
        self.model = agi.GenerativeModel('gemini-2.0-flash')
        self.username = expected_username
    
    def generate_response(self, prompt, chat_history = None):
        user_prompt = prompt.replace("{username}", self.username)

        try:
            if chat_history:
                chat = self.model.start_chat(history=chat_history)
                response = chat.send_message(user_prompt)
            else:
                response = self.model.generate_content(user_prompt)
            
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm having trouble processing that request. Try again later"
    
    def eval_condition(self, user_input, conditions, chat_history=None):
        
        if not conditions:
            return None
        
        process_conditions = [
            condition.replace("{username}", self.username)
            for condition in conditions
        ]
        
        eval_prompt = f"""
        Based on the user's response: "{user_input}"

        Determine if the user id the expected candidate named {self.username} and their readiness.

        Which of the following conditions if true? Respond with  ONLY the matching condition.
        Conditions:
        {', '.join([f'"{c}"' for c in process_conditions])}
        """

        temp = ', '.join([f'"{c}"' for c in process_conditions])
        print(f"-----------{temp}---------------")

        try:
            response = self.model.generate_content(eval_prompt)
            result = response.text.strip()

            for i, condition in enumerate(process_conditions):
                if condition.lower() in result.lower():
                    return conditions[i]
            
            return conditions[0] if conditions else None
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return conditions[0] if conditions else None
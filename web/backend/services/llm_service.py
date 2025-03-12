import os
import google.genai as agi
import google.genai.types as types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

class LLMService:
    def __init__(self, expected_username):
        self.client = agi.Client(
            api_key=GEMINI_API_KEY
        )
        self.model = 'gemini-2.0-flash'
        self.username = expected_username
        self.generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
        )
    
    def generate_response(self, prompt, chat_history = None):
        user_prompt = prompt.format(username=self.username)

        try:
            if chat_history:
                chunks = self.client.models.generate_content_stream(
                    model=self.model,
                    contents=chat_history + [
                        types.Content(
                            role="user", 
                            parts=[types.Part.from_text(text=user_prompt)]
                        )
                    ],
                    config=self.generate_content_config,
                )
            else:
                chunks = self.client.models.generate_content_stream(
                    model=self.model,
                    contents= user_prompt,
                    config=self.generate_content_config,
                )
            
            return chunks
        except Exception as e:
            print(f"Error generating response: {e}")
            raise Exception("I'm having trouble processing that request. Try again later")
    
    def eval_condition(self, user_input, conditions, chat_history=None):
        if not conditions:
            return None
        
        process_conditions = [
            condition.format(username=self.username)
            for condition in conditions
        ]
        
        eval_prompt = f"""
        TASK: Evaluate the user's response to determine which condition is true.

        USER RESPONSE: "{user_input}"

        CONTEXT:
        - Expected candidate name: {self.username}
        - You need to determine if this is the expected candidate and assess their readiness

        INSTRUCTIONS:
        1. Carefully analyze the user's response
        2. Select EXACTLY ONE condition from the list below that best matches the response
        3. Return ONLY the exact text of the matching condition with no additional text
        4. If no condition clearly matches, select the first condition in the list

        CONDITIONS:
        {'\n'.join([f'- "{c}"' for c in process_conditions])}
        """
        
        try:
            chunks = self.client.models.generate_content_stream(
                model=self.model,
                contents= eval_prompt,
                config=self.generate_content_config,
            )
            response = ""
            for chunk in chunks:
                response = response + chunk.text if chunk.text else ""
            result = response.strip()

            for i, condition in enumerate(process_conditions):
                if condition.lower() in result.lower():
                    return conditions[i]
            
            return conditions[0] if conditions else None
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return conditions[0] if conditions else None
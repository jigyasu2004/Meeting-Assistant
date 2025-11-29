import openai
from openai import OpenAI
from utils.logger import logger
from utils.config_manager import config_manager
from llm.prompt_manager import PromptManager

class Translator:
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.api_key = config_manager.get("openai_api_key", "")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def update_api_key(self, key):
        self.api_key = key
        self.client = OpenAI(api_key=key)

    def process(self, transcript):
        # Legacy method for single-turn (kept for compatibility if needed, but we'll switch to history)
        return self.process_with_history([{"role": "user", "content": transcript}])

    def process_with_history(self, messages):
        if not self.client:
            logger.warning("OpenAI API Key not set for LLM.")
            return "Error: API Key missing"

        model = config_manager.get("llm_model", "gpt-3.5-turbo")

        try:
            # Determine token parameter based on model
            token_param = "max_tokens"
            if model.startswith("o1") or "gpt-5" in model:
                token_param = "max_completion_tokens"
            
            # Ensure system message exists if not provided
            if not any(m['role'] == 'system' for m in messages):
                messages.insert(0, {"role": "system", "content": "You are a helpful real-time meeting assistant."})

            kwargs = {
                "model": model,
                "messages": messages,
                token_param: 1000
            }

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return f"Error: {str(e)}"

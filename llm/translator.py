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
        if not self.client:
            logger.warning("OpenAI API Key not set for LLM.")
            return "Error: API Key missing"

        prompt = self.prompt_manager.get_prompt(transcript)
        model = config_manager.get("llm_model", "gpt-3.5-turbo")

        try:
            # Determine token parameter based on model
            # Newer models (o1, gpt-5-nano, etc.) require 'max_completion_tokens'
            # Older models (gpt-3.5, gpt-4) use 'max_tokens'
            token_param = "max_tokens"
            if model.startswith("o1") or "gpt-5" in model:
                token_param = "max_completion_tokens"
            
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                token_param: 1000
            }

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return f"Error: {str(e)}"

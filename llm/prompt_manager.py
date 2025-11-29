from utils.config_manager import config_manager

class PromptManager:
    def __init__(self):
        pass

    def get_prompt(self, transcript):
        template = config_manager.get("prompt_template", "User text:\n{{transcript}}")
        return template.replace("{{transcript}}", transcript)

    def update_template(self, new_template):
        if "{{transcript}}" not in new_template:
            raise ValueError("Template must contain {{transcript}} placeholder")
        config_manager.set("prompt_template", new_template)

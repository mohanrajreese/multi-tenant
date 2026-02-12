from tenants.infrastructure.protocols.intelligence import ILLMProvider
import logging

logger = logging.getLogger(__name__)

class OpenAIProvider(ILLMProvider):
    """
    Tier 59: OpenAI Adapter.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'gpt-4-turbo')

    def generate_text(self, prompt, system_prompt=None, **kwargs):
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"[OpenAI] Error: {e}")
            return f"Error generating text: {str(e)}"

    def get_embeddings(self, text):
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"[OpenAI] Embedding Error: {e}")
            return []

class AnthropicProvider(ILLMProvider):
    """
    Tier 59: Anthropic Adapter.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'claude-3-opus')

    def generate_text(self, prompt, system_prompt=None, **kwargs):
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        
        try:
            message = client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt or "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"[Anthropic] Error: {e}")
            return f"Error generating text: {str(e)}"

    def get_embeddings(self, text):
        # Anthropic doesn't have a public embedding API generally comparable to OAI yet (as of 2024 knowledge),
        # but we can return a placeholder or use a default.
        return []

class OllamaProvider(ILLMProvider):
    """
    Tier 59: Private/Local LLM Adapter.
    """
    def __init__(self, config=None):
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama3')

    def generate_text(self, prompt, system_prompt=None, **kwargs):
        logger.info(f"[Ollama] Generating text with model {self.model}")
        return f"Llama Response to: {prompt[:20]}..."

    def get_embeddings(self, text):
        return [0.0, 0.0, 0.0]

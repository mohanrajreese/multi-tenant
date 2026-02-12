from .providers import OpenAIProvider, AnthropicProvider, OllamaProvider

class LLMFactory:
    """
    Tier 59: Intelligence Resolution Factory.
    """
    @staticmethod
    def get_provider(tenant):
        config = tenant.config.get('intelligence', {})
        provider_type = config.get('provider', 'openai')
        
        if provider_type == 'openai':
            return OpenAIProvider(config)
        elif provider_type == 'anthropic':
            return AnthropicProvider(config)
        elif provider_type == 'ollama':
            return OllamaProvider(config)
            
        return OpenAIProvider(config)

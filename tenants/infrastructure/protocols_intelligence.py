from typing import Protocol, runtime_checkable, Any, List, Dict

@runtime_checkable
class ILLMProvider(Protocol):
    """
    Tier 59: Intelligence Sovereignty Protocol.
    Abstracts Large Language Model interactions.
    """
    def generate_text(self, prompt: str, system_prompt: str = None, **kwargs: Any) -> str:
        """Generate a text completion."""
        ...

    def get_embeddings(self, text: str) -> List[float]:
        """Generate vector embeddings for text."""
        ...

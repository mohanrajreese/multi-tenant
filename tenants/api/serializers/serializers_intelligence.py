from rest_framework import serializers

class IntelligencePromptSerializer(serializers.Serializer):
    """
    Serializer for AI Prompt requests.
    """
    prompt = serializers.CharField(required=True, help_text="The user's input prompt.")
    system_prompt = serializers.CharField(required=False, allow_blank=True, help_text="Optional system context.")
    model = serializers.CharField(required=False, help_text="Override model (if allowed by tenant config).")

class IntelligenceResponseSerializer(serializers.Serializer):
    """
    Serializer for AI Responses.
    """
    response = serializers.CharField(help_text="The AI generated text.")
    model_used = serializers.CharField(help_text="The model that generated the response.")

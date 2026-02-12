from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # The tenant is automatically injected by the ViewSet/Service
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)

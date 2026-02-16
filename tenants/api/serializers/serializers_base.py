from rest_framework import serializers

class TenantAwareSerializer(serializers.ModelSerializer):
    """
    Base serializer for all tenant-scoped models.
    Ensures consistent handling of tenant isolation fields if needed.
    """
    pass

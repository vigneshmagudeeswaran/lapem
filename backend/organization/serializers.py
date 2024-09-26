from rest_framework import serializers
from organization.models import Organization



class OrganizationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
    is_subscribed = serializers.BooleanField(required=False)
    subscription_start=serializers.DateTimeField(required=False)
    subscription_extended=serializers.BooleanField(required=False)
    subscription_end=serializers.DateTimeField(required=False)
    email = serializers.EmailField()
    created = serializers.DateTimeField(required=False)
    class Meta:
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        return Organization.objects.create(**validated_data)
    
    
    
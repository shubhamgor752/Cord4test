from rest_framework import serializers

from .models import Connection


class FolloweSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = '__all__'


        extra_kwargs = {
            "user": {"required": False}}

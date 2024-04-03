from rest_framework import serializers
from .models import Post


class createpostSerializer(serializers.Serializer):
    description = serializers.CharField()





class ListpostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = ['author', 'description']
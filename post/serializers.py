from rest_framework import serializers
from .models import Post, Comment


class createpostSerializer(serializers.Serializer):
    description = serializers.CharField()




class CreateCommentSerializer(serializers.ModelSerializer):
    class  Meta:
        model=Comment
        fields = ["post", "comment", "author"]

        extra_kwargs = {
            "author": {"required": False},
        }
    def validate_post_id(self, value):
        try:
            int(value)
        except ValueError:
            raise serializers.ValidationError("The id must be an integer")
        
        # Check if the user exist
class LikePostSerializer(serializers.Serializer):
    post_id = serializers.CharField()

class ListpostSerializer(serializers.ModelSerializer):
    comments = CreateCommentSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = ['author', 'description', 'comments']
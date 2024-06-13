from rest_framework import serializers
from .models import CustomGroup, GroupChat

from Register.models import CustomUser


class GroupSerializer(serializers.ModelSerializer):
   
    class Meta: 
        model = CustomGroup
        fields = ["group_name", "group_admins", "members", "is_private"]
        extra_kwargs = {
            "group_admins": {
                "required": False,
                "allow_empty": True
            }
        }


    def validate_group_name(self, value):
        """
        Check if the group name already exists.
        """
        if self.instance:
            # If an instance is being updated, then it's okay for the group name to be unchanged.
            if CustomGroup.objects.exclude(pk=self.instance.pk).filter(group_name=value).exists():
                raise serializers.ValidationError("Group name already exists.")
        else:
            # If creating a new instance, check if the group name already exists.
            if CustomGroup.objects.filter(group_name=value).exists():
                raise serializers.ValidationError("Group name already exists.")
        return value

    def validate_group_admins(self, value):
        """
        Check if the admins are also members of the group.
        """
        members = self.initial_data.get("members", [])
        for admin in value:
            if admin not in members:
                raise serializers.ValidationError("Group admin must also be a member of the group.")
        return value

    def validate_members(self, value):
        """
        Check if all members are unique and there is at least one member.
        """
        if len(value) < 1:
            raise serializers.ValidationError("At least one member is required.")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("All members must be unique.")
        return value


class GroupMessagesSerializer(serializers.ModelSerializer):
    group_admins = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = CustomGroup
        fields = (
            "id",
            "group_name",
            "group_admins",
            "members",
            "is_private",
        )

    def get_group_admins(self, obj):
        return [admin.username for admin in obj.group_admins.all()]

    def get_members(self, obj):
        return [member.username for member in obj.members.all()]


class AddGroupMemberSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    members_id = serializers.IntegerField()


class JoinRequesGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    is_accept = serializers.BooleanField(default=False)


# class GroupchatSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GroupChat
#         fields = '__all__'


#         extra_kwargs = {
#             'group': {"required":False},
#             'receivers' : {"required":False}
#         }

class GroupchatSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    message = serializers.CharField()


class GroupMessageListSerialzers(serializers.Serializer):
    group_id = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    receivers = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    def get_sender(self, obj):
        return obj.sender.username

    def get_receivers(self, obj):
        return [receiver.username for receiver in obj.receivers.all()]

    def get_message(self, obj):
        return obj.message_content

    def get_group_id(self, obj):
        return obj.group.id

    def get_group_name(self, obj):
        return obj.group.group_name
    
    def get_timestamp(self, obj):
        return obj.timestamp

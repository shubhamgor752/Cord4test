from rest_framework import serializers
from .models import Post, Comment, EventPost, Ticket, TicketPurchase


class createpostSerializer(serializers.Serializer):
    post_title = serializers.CharField()
    description = serializers.CharField()

    def update(self, instance, validated_data):
        instance.post_title = validated_data.get("post_title", instance.post_title)
        instance.description = validated_data.get("description", instance.description)

        instance.save()

        return instance


class CreateCommentSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    comment = serializers.CharField()



    # class  Meta:
    #     model=Comment
    #     fields = ["post", "comment", "author"]

    #     extra_kwargs = {
    #         "author": {"required": False},
    #     }
    # def validate_post_id(self, value):
    #     try:
    #         int(value)
    #     except ValueError:
    #         raise serializers.ValidationError("The id must be an integer")

    # Check if the user exist
class LikePostSerializer(serializers.Serializer):
    post_id = serializers.CharField()


class LikeViewSerializer(serializers.Serializer):
    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return [user.username for user in obj.likes.all()]


class ListpostSerializer(serializers.ModelSerializer):
    comments = CreateCommentSerializer(many=True, read_only=True)
    likes = LikeViewSerializer(source='*')
    author = serializers.StringRelatedField()

    def get_comment_name(self,obj):
        return obj.author.username

    class Meta:
        model = Post
        fields = ['author', 'description', 'comments','likes']


class EventPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPost
        fields = [
            "title",
            "description",
            "event_type",
            "event_date",
            "event_end_date",
            "event_location",
            # "author",
        ]

    def validate(self, data):
        event_type = data.get("event_type")
        ticket_price = data.get("ticket_price")

        if event_type == EventPost.FREE and ticket_price is not None:
            raise serializers.ValidationError(
                "Ticket price should not be provided for a free event."
            )
        elif event_type == EventPost.PAID and ticket_price is None:
            raise serializers.ValidationError(
                "Ticket price is required for a paid event."
            )

        return data


# class EventPostCreateSerializer(serializers.Serializer):
#     title = serializers.CharField(max_length=255)
#     description = serializers.CharField()
#     event_type = serializers.ChoiceField(choices=EventPost.EVENT_TYPE_CHOICES)
#     event_date = serializers.DateField()
#     event_location = serializers.CharField(max_length=255)
#     ticket_price = serializers.DecimalField(
#         max_digits=10, decimal_places=2, required=False
#     )

#     def validate(self, data):
#         event_type = data.get("event_type")
#         ticket_price = data.get("ticket_price")

#         if event_type == EventPost.FREE and ticket_price is not None:
#             raise serializers.ValidationError(
#                 "Ticket price should not be provided for a free event."
#             )
#         elif event_type == EventPost.PAID and ticket_price is None:
#             raise serializers.ValidationError(
#                 "Ticket price is required for a paid event."
#             )

#         return data

#     def create(self, validated_data):
#         return EventPost.objects.create(**validated_data)


class JoinEventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()


class TicketSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    ticket_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    author = serializers.CharField(max_length=100, required=False)
    available_quantity = serializers.IntegerField()

    # class Meta:
    #     model = Ticket
    #     fields = ("event", "ticket_price", "customer", "quantity")


class TicketListSerializer(serializers.Serializer):
    title = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()
    ticket_price = serializers.SerializerMethodField()

    def get_title(self,obj):
        return obj.event.title

    def get_ticket_price(self, obj):
        return obj.ticket_price

    def get_author(self, obj):
        return obj.author.username

    def get_available_quantity(self, obj):
        return obj.available_quantity


class TicketPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketPurchase
        fields = ["ticket", "quantity"]

        extra_kwargs = {"user": {"required": False}}


class TickerOrderSerializer(serializers.Serializer):

    user = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()
    purchase_date = serializers.SerializerMethodField()

    def get_title(self, obj):
        return obj.ticket.event.title

    def get_user(self, obj):
        return obj.user.username

    def get_quantity(self, obj):
        return obj.quantity

    def get_order_id(self, obj):
        return obj.order_id

    def get_purchase_date(self, obj):
        return obj.purchase_date

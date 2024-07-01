from django.contrib import admin
from .models import Post, Comment, EventPost, Ticket, TicketPurchase , Poll

# Register your models here.


class postadmin(admin.ModelAdmin):
    fields = ["id", "author", "likes","description"]
    list_display = ["id", "author", "post_title",  "description","get_like_display"]

    def get_like_display(self,obj):
        return ", ".join(like.username for like in obj.likes.all())

    get_like_display.short_description = 'Likes'

admin.site.register(Post,postadmin)


class commentadmin(admin.ModelAdmin):
    fields = ["posttitle","comment","author"]

    list_display = ["id","get_post_name", "comment", "author"]

    def get_post_name(self, obj):
        return obj.post.post_title

    get_post_name.short_description = "Post Name"


admin.site.register(Comment,commentadmin)


class evntadmin(admin.ModelAdmin):
    fields = [
        "title",
        "author",
        "likes",
        "description",
        "event_type",
        "event_date",
        "event_end_date",
        "event_location",
        # "ticket_price",
        "joining_users",
    ]
    list_display = [
        "id",
        "author",
        "title",
        "description",
        "event_type",
        "event_date",
        "event_end_date",
        "event_location",
        # "ticket_price",
        "get_attendees_display",
    ]

    def get_attendees_display(self, obj):
        return ", ".join([attendees.username for attendees in obj.joining_users.all()])

    get_attendees_display.short_description = "joining_users"


admin.site.register(EventPost,evntadmin)


class ticketadmin(admin.ModelAdmin):
    fields = ["event", "ticket_price", "available_quantity"]
    list_display = ["id","author", "get_event_name", "available_quantity", "ticket_price"]

    
    def get_event_name(self, obj):
        return obj.event.title
    get_event_name.short_description = "Event Name"

admin.site.register(Ticket, ticketadmin)


class tickerpurchaseadmin(admin.ModelAdmin):
    fields = ["ticket", "user", "quantity", "order_id"]
    list_display = [
        "id",
        "get_event_name",
        "user",
        "quantity",
        "order_id" ,
        "purchase_date",
    ]

    def get_event_name(self, obj):
        return obj.ticket.event.title
    get_event_name.short_description = "Ticket__title"

admin.site.register(TicketPurchase,tickerpurchaseadmin)




class polladmin(admin.ModelAdmin):
    fields = ["author", "question", "options"]
    list_display = ["id", "author", "question", "options"]



admin.site.register(Poll, polladmin)
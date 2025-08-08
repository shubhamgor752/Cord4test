from django.db import models
from Register.models import UserProfile,CustomUser

# Create your models here.


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    post_title = models.CharField(max_length=55)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE , related_name='create_post')
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)
    description = models.TextField()


class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    comment = models.TextField()
    author = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    # created_at = models.DateTimeField(auto_now_add=True)


class EventPost(Post):
    FREE = "free"
    PAID = "paid"
    EVENT_TYPE_CHOICES = [
        (FREE, "Free Event"),
        (PAID, "Paid Event"),
    ]
    title = models.CharField(max_length=55)
    event_type = models.CharField(max_length=4, choices=EVENT_TYPE_CHOICES)
    event_date = models.DateField()
    event_end_date = models.DateField()
    event_location = models.CharField(max_length=255)
   

    joining_users = models.ManyToManyField(
        CustomUser, related_name="attended_events", blank=True
    )


class Ticket(models.Model):
    event = models.ForeignKey("EventPost", on_delete=models.CASCADE)
    ticket_price = models.PositiveIntegerField(
    blank=True,
    null=True,
    help_text="Enter the ticket price in cents.",
    )
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    available_quantity = models.IntegerField()


class TicketPurchase(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_id = models.CharField(max_length=100, unique=True)

    purchase_date = models.DateTimeField(auto_now_add=True)


class Poll(models.Model):
    author= models.ForeignKey(CustomUser, on_delete=models.CASCADE , related_name='create_poll_ppost')
    question = models.CharField(max_length=255)
    options = models.JSONField()

    def __str__(self):
        return self.question


class PollAnswer(models.Model):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    votedby_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='poll_answers'
    )
    selected_option = models.CharField(max_length=255)
    # answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'votedby_user')  # Prevent duplicate votes

    def __str__(self):
        return f"{self.user} voted '{self.selected_option}' on '{self.poll.question}'"
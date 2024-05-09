from celery import shared_task
from datetime import datetime, time, timedelta
from Register.models import CustomUser
from .views import SendMessageViewSet


# @shared_task
# def send_daily_message():
#     users = CustomUser.objects.all()

#     print(users)

#     send_time = time(hour=11, minute=0, second=0)
#     today = datetime.now().date()
#     schedule_time = datetime.combine(today, send_time)

#     if schedule_time < datetime.now():
#         schedule_time += timedelta(days=1)

#     for user in users:
#         SendMessageViewSet().create(
#             request=None,
#             receiver=user.id,
#             message="Your scheduled message here",
#             schedule_time=schedule_time,
#         )


@shared_task
def send_daily_message():
    users = CustomUser.objects.all()

    print(users)

    today = datetime.now().date()

    for user in users:
        SendMessageViewSet().create(
            request=None,
            receiver=user.id,
            message="Your scheduled message here",
            schedule_time=today,  # Sending on the same day
        )



# @shared_task
# def process_daily_message():
#     users = CustomUser.objects.all()

#     for user in users:

import datetime
from pytz import timezone
from datetime import timedelta
from .models import *
from .views_cutomer import send_notification
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.models import Q

tz = timezone("Asia/Kolkata")


def remind_doctors_appointment():
    today = datetime.datetime.now()
    obj = Add_Pet_Reminder.objects.filter(select_date=today.date(),
                                          select_time__contains=today.time().strftime('%H:%M'))
    for i in obj:
        message_body = f'{i.fk_user.name}, you have an appointment for {i.fk_pet.pet_name}.'
        send_notification(message_body, i.fk_user.token, 'Admin', 'Appointment Reminder', i.fk_user.id)


def notify_doctors_appointment_completion():
    today = datetime.datetime.now()
    mins_30 = today + timedelta(minutes=30)

    obj = DoctorsAppointment.objects.filter(booking_date__lte=mins_30.date(),
                                            booking_time__lte=mins_30.time()).exclude(Q(book_status='Completed') | Q(book_status='Cancelled'))
    DoctorsAppointment.objects.filter(booking_date__lte=today.date(), booking_time__lte=today.time()).exclude(Q(book_status='Completed') | Q(book_status='Cancelled')).update(
        book_status='Completed')
    for i in obj:
        message_body = f'Congratulations your appointment is now completed!'
        send_notification(message_body, i.doctor.token, 'Admin', 'Appointment completed', i.doctor.id)
        send_notification(message_body, i.client.token, 'Admin', 'Appointment completed', i.client.id)
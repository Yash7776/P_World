from operator import itemgetter
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from datetime import datetime
import json
import traceback
import random
import base64
from rest_framework.decorators import api_view, permission_classes
import requests
from rest_framework import status
from .serializers import *
import ast
from django.core.mail import send_mail
import string
import secrets
from django.db import transaction
import yaml
from google.oauth2 import service_account
from google.auth.transport.requests import Request

###################### Upload image #####################
def upload_image(img, img_path, img_name):
    path = settings.BASE_DIR + "/media/"
    # path = "/media/"
    random_number = '{:04}'.format(random.randrange(1, 10 ** 4))
    imgN = img_path + img_name + random_number + "_" + '.jpg'
    destination = open(path + imgN, 'wb')
    # img = img.resize((1000, 1000), Image.ANTIALIAS)   
    destination.write(base64.b64decode(img))
    destination.close()
    return imgN


##########################################################
FIREBASE_PROJECT_ID = "pworld-352a9"
SERVICE_ACCOUNT_FILE = "firebase_service_account.json"


def get_fcm_access_token():
    SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    credentials.refresh(Request())
    return credentials.token


def send_notification(message_body, token, sender, notification_title, uid, type):
    message_title = "PWorld"

    if not token:
        print("❌ FCM Error: Token is empty or None")
        return False

    try:
        access_token = get_fcm_access_token()

        url = f"https://fcm.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/messages:send"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "message": {
                "token": token,
                "notification": {
                    "title": message_title,
                    "body": message_body
                },
                "data": {
                    "title": notification_title,
                    "body": message_body,
                    "sender": sender,
                    "action": "NewLoadProposal",
                    "android_channel_id": "noti_push_app_1",
                    "sound": "alarm.mp3",
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    "type": str(type)
                },
                "android": {
                    "notification": {
                        "channel_id": "noti_push_app_1",
                        "sound": "alarm"
                    }
                }
            }
        }

        print("📤 Sending FCM v1 Notification...")
        print("➡️ Payload:", json.dumps(payload, indent=2))

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        print("📥 FCM Response Status:", response.status_code)
        print("📥 FCM Response Body:", response.text)

        if response.status_code == 200:
            Notification.objects.create(
                title=notification_title,
                notification=message_body,
                receiver_id=uid,
                date=datetime.now()
            )

            print("✅ Notification sent and saved successfully")
            return True

        else:
            print("❌ FCM Failed")
            return False

    except requests.exceptions.Timeout:
        print("⏱️ FCM Error: Request timed out")
        return False

    except requests.exceptions.RequestException as e:
        print("❌ FCM Request Exception:", str(e))
        traceback.print_exc()
        return False

    except Exception as e:
        print("🔥 Unexpected Error while sending notification:", str(e))
        traceback.print_exc()
        return False

        

def forgot_password_email(name, email):
    print("---- FORGOT PASSWORD EMAIL FUNCTION ----")
    print("Name:", name)
    print("Email:", email)

    try:
        alphabet = string.ascii_letters + string.digits
        new_password = ''.join(secrets.choice(alphabet) for i in range(8))
        print("Generated password:", new_password)

        mail_subject = "P World password recovery mail"
        from_email = settings.EMAIL_HOST_USER

        print("From email:", from_email)
        print("EMAIL HOST:", settings.EMAIL_HOST)
        print("EMAIL PORT:", settings.EMAIL_PORT)
        print("EMAIL USE TLS:", settings.EMAIL_USE_TLS)

        message = (
            f"Hi, {name}\n"
            f"You are receiving this mail because we received a forgot password request.\n"
            f"Your new password is: {new_password}\n\n"
            f"Do not share your password.\n\n"
            f"Thanks,\nP World"
        )

        print("Attempting to send email...")
        send_mail(mail_subject, message, from_email, [email])
        print("Email sent successfully")

        return new_password

    except Exception as e:
        print("---- EXCEPTION IN forgot_password_email ----")
        print(str(e))
        print(traceback.format_exc())
        raise



#get_uesr_details
@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_uesr_details(request):
    try:
        data = request.data
        response = Response()
        email = data['email']
        password = data['password']

        if User_Details.objects.filter(email=email, password=password).exists():

            cus_obj = User_Details.objects.get(email=email, password=password)

            pro_image = str(cus_obj.profile_image.url) if cus_obj.profile_image else ""

            return Response(
                {'status': 200, "msg": 'User details', "user_id": cus_obj.id, "user_type": cus_obj.user_type,
                 "name": cus_obj.name, "email": cus_obj.email, "mobile_no": cus_obj.mobile_no,
                 "address": cus_obj.address, "country_code": cus_obj.country_code,
                 "map_location": cus_obj.map_location, "latitude": cus_obj.latitude, "longitude": cus_obj.longitude,
                 'pro_image': pro_image})
        else:
            return Response({'status': 403, "msg": 'Invalid Credential'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def cutomer_signup_api(request):
    try:
        data = request.data
        response = Response()
        mobile_no = data['mobile_no']
        email = data['email']
        mobile_otp = "1234"

        if User_Details.objects.filter(email=email).exists():
            return Response({'status': 403, "msg": 'Email is Already Resgistered'})
        elif User_Details.objects.filter(mobile_no=mobile_no).exists():
            return Response({'status': 403, "msg": 'Mobile No is Already Resgistered'})
        else:
            return Response({'status': 200, "msg": 'Click on Ok to receive OTP at your registered mobile number',
                             "mobile_otp": mobile_otp, 'mobile_no': mobile_no})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def create_account_customer(request):
    try:
        data = request.data
        response = Response()
        user_type = data['user_type']
        sign_up_status = data['sign_up_status']
        name = data['name']
        email = data['email']
        password = data['password']
        mobile_no = data['mobile_no']
        country_data = data['country_code']
        map_location = data['map_location']
        latitude = data['latitude'] 
        longitude = data['longitude']
        address = data['address']
        token = data['token'] 


        # -------------------------
        # LOCATION (Default Nagpur)
        # -------------------------
        DEFAULT_LATITUDE = '21.118064'
        DEFAULT_LONGITUDE = '79.0450328'

        latitude = data.get('latitude') or DEFAULT_LATITUDE
        longitude = data.get('longitude') or DEFAULT_LONGITUDE
       
        country_code, sortname = country_data.split(',')
        country_obj = CountryMaster.objects.get(country_code = country_code[1:],sortname=sortname) 

        if User_Details.objects.filter(email=email).exists():
            return Response({'status': 403, "msg": 'Email is Already Registered'})
        elif User_Details.objects.filter(mobile_no=mobile_no).exists():
            return Response({'status': 403, "msg": 'Mobile No is Already Registered'})
        else:
            User_obj = User_Details(password=password, mobile_no=mobile_no, email=email, name=name,sign_up_status=sign_up_status, user_type=user_type, map_location=map_location,latitude=latitude, longitude=longitude, status=True, token=token,country_code=country_code,created_datetime=datetime.now(), address=address,country = country_obj.name)

            User_obj.save() 
            request.session['customer_email'] =  email
            request.session['customer_id'] =  User_obj.id 
            request.session['user_type'] =  user_type
            return Response({'status': 200, "msg": 'Account Created Successfully', "customer_id": User_obj.id,
                             "user_type": User_obj.user_type, "name": User_obj.name, "email": User_obj.email,
                             "mobile_no": User_obj.mobile_no, "map_location": User_obj.map_location,
                             "latitude": User_obj.latitude, "longitude": User_obj.longitude, 'pro_image': "",
                             "user_type" : User_obj.user_type})

    except:
        traceback.print_exc()
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def login_customer_api(request):
    try:
        data = request.data
        response = Response()
        email = data['email']
        password = data['password']
        token = data['token']
        if User_Details.objects.filter(email=email, password=password).exists():
            cus_obj = User_Details.objects.get(email=email, password=password)
            if token != '':
                cus_obj.token = token
                cus_obj.save()
            request.session['customer_email'] = cus_obj.email
            request.session['customer_id'] = cus_obj.id
            request.session['user_type'] = cus_obj.user_type
            
            return Response(
                {'status': 200, "msg": 'Login Successful', "user_id": cus_obj.id, "user_type": cus_obj.user_type,
                 "name": cus_obj.name, "email": cus_obj.email, "mobile_no": cus_obj.mobile_no, "token": token,
                 "map_location": cus_obj.map_location, "latitude": cus_obj.latitude, "longitude": cus_obj.longitude})
        else:
            return Response({'status': 403, "msg": 'Invalid Credential'})
    except:
        traceback.print_exc()
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def add_new_pet_api(request):
    try:
        data = request.data
        response = Response()
        customer_id = data['fk_customer']
        pet_name = data['pet_name']
        type_of_pet = data['type_of_pet']
        breed = data['breed']
        birth_date = data['birth_date']
        gender = data['gender']
        weight = data['weight']
        pet_description = data['pet_description']
        pet_image = data['pet_image']

        if pet_image:
            profile_upload_image = upload_image(pet_image, "pet_image/", "profile_")
        else:
            profile_upload_image = ""

        obj = New_Pet(pet_name=pet_name, type_of_pet=type_of_pet, breed=breed, birth_date=birth_date, gender=gender,
                      weight=weight, pet_description=pet_description, created_datetime=datetime.now(),
                      fk_customer_id=customer_id, pet_image=profile_upload_image)
        obj.save()

        return Response({'status': 200, "msg": 'New Pet Added Successfully', "pet_id": obj.id})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


from datetime import date
from datetime import datetime


def cal_age(birth_date):
    now = datetime.now()
    nowyear = now.strftime("%Y")
    nowmonth = now.strftime("%m")
    year = int(nowyear)
    month = int(nowmonth)
    age = ""
    x = birth_date.split("-")
    y = str(x)
    p_yr = int(x[0])
    p_month = int(x[1])
    day = int(x[2])

    if (p_yr < year):
        if (p_month < month):
            x = year - p_yr
            y = month - p_month
            if x != 0:
                age = f"{x} year {y} month"
            else:
                age = f"{y} month"
            print(f"your age is {x} year and {y} months")
        else:
            x = (year - p_yr) - 1
            y = 12 - (p_month - month)
            if x != 0:
                age = f"{x} year {y} month"
            else:
                age = f"{y} month"
            print(f"your age is {x} year and {y} months")
    else:
        y = month - p_month
        age = f"{y} month"
    return age


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_pet_list(request):
    try:
        data = request.data
        response = Response()
        customer_id = data['customer_id']
        list = []
        dict = {}
        if User_Details.objects.filter(id=customer_id).exists():
            if New_Pet.objects.filter(fk_customer_id=customer_id).exists():
                obj = New_Pet.objects.filter(fk_customer_id=customer_id)
                for i in obj:
                    dict['pet_id'] = i.id
                    dict['pet_name'] = i.pet_name
                    dict['type_of_pet'] = i.type_of_pet
                    dict['breed'] = i.breed
                    dict['birth_date'] = i.birth_date
                    age = cal_age(str(i.birth_date))
                    dict['age'] = age
                    dict['gender'] = i.gender
                    dict['weight'] = i.weight
                    dict['pet_description'] = i.pet_description
                    dict['pet_image'] = str(i.pet_image)
                    list.append(dict)
                    dict = {}
                return Response({'status': 200, "msg": 'Customer pet list', "pet_list": list})
            else:
                return Response({'status': 403, "msg": 'No pet details available'})
        else:
            return Response({'status': 403, "msg": 'No customer detail found'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def Edit_pet_api(request):
    try:
        data = request.data
        response = Response()
        pet_id = data['pet_id']
        pet_name = data['pet_name']
        type_of_pet = data['type_of_pet']
        breed = data['breed']
        birth_date = data['birth_date']
        gender = data['gender']
        weight = data['weight']
        pet_description = data['pet_description']
        pet_image = data['pet_image']

        if New_Pet.objects.filter(id=pet_id).exists():
            pet_obj = New_Pet.objects.get(id=pet_id)
            if pet_image:
                upload_new_pet_image = upload_image(pet_image, "pet_image/", "profile_")
                pet_obj.pet_image = upload_new_pet_image
                pet_obj.save()

            New_Pet.objects.filter(id=pet_id).update(pet_name=pet_name, type_of_pet=type_of_pet,
                                                     breed=breed, birth_date=birth_date, gender=gender,
                                                     weight=weight, pet_description=pet_description)

            return Response({'status': 200, "msg": 'Pet is updated successfully', "pet_id": pet_obj.id})
        else:

            return Response({'status': 403, "msg": 'No Pet details found.'})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def delete_pet_api(request):
    try:
        data = request.data
        response = Response()
        pet_id = data['pet_id']

        if New_Pet.objects.filter(id=pet_id).exists():

            update_doc_obj = New_Pet.objects.filter(id=pet_id).delete()

            return Response({'status': 200, "msg": 'Pet details deleted successfully'})
        else:
            return Response({'status': 403, "msg": 'No Pet detail found.'})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# @csrf_exempt
# def add_reminder_pet_api(request):
#     try:
#         data = request.data
#         response = Response()
#         customer_id = data['fk_customer']
#         pet_id = data['pet_id']
#         reminder_name = data['reminder_name']
#         select_date = data['select_date']
#         select_time = data['select_time']
         
#         print(customer_id)
#         if User_Details.objects.filter(id=customer_id).exists():

#             if New_Pet.objects.filter(id=pet_id).exists():

#                 obj = Add_Pet_Reminder(fk_user_id=customer_id, fk_pet_id=pet_id, reminder_name=reminder_name,
#                                        select_date=select_date, select_time=select_time)
#                 obj.save()
#             else:
#                 return Response({'status': 403, "msg": 'No Pet detail found.'})

#             return Response({'status': 200, "msg": 'Pet Reminder Added Successfully', "rem_id": obj.id})
#         else:
#             return Response({'status': 403, "msg": 'No customer detail found.'})

#     except:
#         print(str(traceback.format_exc()))
#         return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})
@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def add_reminder_pet_api(request):
    try:
        data = request.data

        customer_id = data.get('fk_customer')
        pet_id = data.get('pet_id')
        reminder_name = data.get('reminder_name')
        select_date = data.get('select_date')
        select_time = data.get('select_time')

        # Validate required fields
        if not all([customer_id, pet_id, reminder_name, select_date, select_time]):
            return Response({
                'status': 400,
                'msg': 'Required fields missing',
                'missing': [
                    key for key in ['fk_customer', 'pet_id', 'reminder_name', 'select_date', 'select_time']
                    if not data.get(key)
                ]
            })

        if not User_Details.objects.filter(id=customer_id).exists():
            return Response({'status': 403, 'msg': 'No customer detail found.'})

        if not New_Pet.objects.filter(id=pet_id).exists():
            return Response({'status': 403, 'msg': 'No Pet detail found.'})

        obj = Add_Pet_Reminder(
            fk_user_id=customer_id,
            fk_pet_id=pet_id,
            reminder_name=reminder_name,
            select_date=select_date,
            select_time=select_time
        )
        obj.save()

        return Response({
            'status': 200,
            'msg': 'Pet Reminder Added Successfully',
            'rem_id': obj.id
        })

    except Exception as e:
        print(traceback.format_exc())
        return Response({
            'status': 500,
            'msg': 'Something went wrong',
            'error': str(e)
        })


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def update_reminder_pet_api(request):
    try:
        data = request.data
        response = Response()
        rem_id = data['rem_id']
        reminder = data['reminder_name']
        date = data['select_date']
        select_time = data['select_time']

        if Add_Pet_Reminder.objects.filter(id=rem_id).exists():

            obj = Add_Pet_Reminder.objects.get(id=rem_id)

            obj.reminder_name = reminder
            obj.select_date = date
            obj.select_time = select_time
            obj.save()

            return Response(
                {'status': 200, "msg": 'Pet Reminder updated Successfully', "rem_id": obj.id, "pet_id": obj.fk_pet.id})
        else:
            return Response({'status': 403, "msg": 'Reminder not found'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def delete_reminder_pet_api(request):
    try:
        data = request.data
        response = Response()
        reminder_id = data['reminder_id']

        if Add_Pet_Reminder.objects.filter(id=reminder_id).exists():

            update_doc_obj = Add_Pet_Reminder.objects.filter(id=reminder_id).delete()

            return Response({'status': 200, "msg": 'Pet reminder is deleted successfully'})
        else:
            return Response({'status': 403, "msg": 'No Pet detail found.'})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# @csrf_exempt
# def get_reminder_pet_list(request):
#     try:
#         data = request.data
#         response = Response()
#         customer_id = data['customer_id']
#         reminder_date = data['reminder_date']
#         list = []
#         dict = {}

#         if User_Details.objects.filter(id=customer_id).exists():

#             if Add_Pet_Reminder.objects.filter(fk_user_id=customer_id).exists():

#                 obj = Add_Pet_Reminder.objects.filter(fk_user_id=customer_id,select_date = reminder_date)
#                 if obj.exists():
#                     for i in obj:

#                         dict['pet_id'] = i.fk_pet.id
#                         dict['rem_id'] = i.id
#                         dict['reminder_name'] = i.reminder_name
#                         dict['select_date'] = i.select_date

#                         try:
#                             d = datetime.strptime(i.select_time, "%H:%M")
#                             time = d.strftime("%I:%M %p")
#                         except:
#                             time = i.select_time

#                         dict['select_time'] = time
#                         dict['pet_image'] = str(i.fk_pet.pet_image) if i.fk_pet.pet_image else ""
#                         dict['petname'] = i.fk_pet.pet_name if i.fk_pet.pet_name else ""
#                         # s
#                         list.append(dict)
#                         dict = {}

#                     return Response({'status': 200, "msg": 'Reminder pet list', "Reminder pet_list": list})
#                 else:
#                     return Response({'status': 403, "msg": 'No Pet reminder found.'})
#             else:
#                 return Response({'status': 403, "msg": 'No Pet reminder found.'})
#         else:
#             return Response({'status': 403, "msg": 'No customer detail found.'})

#     except:
#         print(str(traceback.format_exc()))
#         return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})
from datetime import datetime, date, time as dtime
import traceback

from datetime import datetime, date, time as dtime
import traceback

@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_reminder_pet_list(request):
    try:
        print("\n=========== REMINDER API CALLED ===========")

        data = request.data
        customer_id = data.get('customer_id')
        reminder_date = data.get('reminder_date')  # optional

        print("Customer ID:", customer_id)
        print("Reminder Date Input:", reminder_date)

        if not customer_id:
            return Response({'status': 403, 'msg': 'customer_id required'})

        if not User_Details.objects.filter(id=customer_id).exists():
            return Response({'status': 403, 'msg': 'No customer detail found.'})

        qs = Add_Pet_Reminder.objects.filter(fk_user_id=customer_id)
        print("Total reminders for user:", qs.count())
        print("All DB dates:", list(qs.values_list("select_date", flat=True)))

        # ✅ Normalize date string
        if reminder_date:
            reminder_date = str(reminder_date).strip()   # remove spaces
            reminder_date = reminder_date.split("T")[0]  # remove time if any

            print("Normalized reminder date:", reminder_date)

            qs = Add_Pet_Reminder.objects.filter(
                fk_user_id=customer_id,
                select_date__icontains=reminder_date   # safe match
            )

            print("Reminders after date filter:", qs.count())
            print("Matched DB dates:", list(qs.values_list("select_date", flat=True)))

        if not qs.exists():
            return Response({
                'status': 200,
                'msg': 'No Pet reminder found.',
                'upcoming_list': [],
                'expired_list': []
            })

        today = date.today()
        now_time = datetime.now().time()

        upcoming = []
        expired = []

        for r in qs:
            reminder_date_db = r.select_date
            reminder_time = r.select_time or dtime(0, 0)

            item = {
                'pet_id': r.fk_pet.id if r.fk_pet else None,
                'rem_id': r.id,
                'reminder_name': r.reminder_name,
                'select_date': r.select_date,
                'select_time': str(r.select_time) if r.select_time else "",
                'pet_image': str(r.fk_pet.pet_image) if r.fk_pet and r.fk_pet.pet_image else "",
                'petname': r.fk_pet.pet_name if r.fk_pet else "",
            }

            if reminder_date_db < today:
                expired.append((reminder_date_db, reminder_time, item))
            elif reminder_date_db > today:
                upcoming.append((reminder_date_db, reminder_time, item))
            else:
                if reminder_time < now_time:
                    expired.append((reminder_date_db, reminder_time, item))
                else:
                    upcoming.append((reminder_date_db, reminder_time, item))

        upcoming.sort(key=lambda x: (x[0], x[1]))
        expired.sort(key=lambda x: (x[0], x[1]), reverse=True)

        print("Upcoming:", len(upcoming))
        print("Expired:", len(expired))
        print("=========== REMINDER API END ===========\n")

        return Response({
            'status': 200,
            'msg': 'Reminder pet list',
            'upcoming_list': [i[2] for i in upcoming],
            'expired_list': [i[2] for i in expired],
        })

    except Exception as e:
        traceback.print_exc()
        return Response({
            'status': 403,
            'msg': 'Something went wrong',
            'error': str(e)
        })






@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def Reminder_On_Off(request):
    try:
        data = request.data

        if Add_Pet_Reminder.objects.filter(id = data['reminder_id']).exists():
            Add_Pet_Reminder.objects.filter(id = data['reminder_id']).update(reminder_status = data['reminder_status'])
            return Response({'status':200,'msg':'Reminder Status Changed Successfully.'})
        else:
            return Response({'status':403,'msg':'No Pet reminder found.'})
        
    except:
        traceback.print_exc()
        return Response({'status':403,'msg':'Something went wrong.'})

######################################LIST of ALL Doctors##################################################

from math import sin, cos, sqrt, atan2, radians

@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_all_doctors_list(request):
    try:
        print("\n================= GET ALL DOCTORS LIST API CALLED =================")

        data = request.data
        print("Request Data:", data)

        current_lat = data.get('current_lat')
        current_long = data.get('current_long')
        client_id = data.get('client_id')

        print("Current Lat:", current_lat)
        print("Current Long:", current_long)
        print("Client ID:", client_id)

        distance_limit = 50.0  
        print("Distance Limit:", distance_limit)

        dr_lst, trainer_lst, sitter_lst, walker_lst, salon_lst = [], [], [], [], []

        # ================= DISTANCE QUERY =================
        if current_lat and current_long:
            print("\n📍 Location provided → Running distance query")

            query = f"""
            SELECT 
                t.id,
                t.user_type,
                t.latitude,
                t.longitude,
                (
                    6371 * acos(
                        cos(radians({current_lat})) *
                        cos(radians(t.latitude)) *
                        cos(radians(t.longitude) - radians({current_long})) +
                        sin(radians({current_lat})) *
                        sin(radians(t.latitude))
                    )
                ) AS distance_km
            FROM Pword_db.P_World_App_user_details t
            WHERE t.user_type != 'Customer'
            HAVING distance_km <= {distance_limit}
            ORDER BY distance_km ASC
            """

            print("Distance Query:\n", query)
            result = User_Details.objects.raw(query)
        else:
            print("\n📍 Location NOT provided → Fetching all non-customer users")
            result = User_Details.objects.exclude(user_type="Customer")

        result_list = list(result)
        print("\n🔢 Total users fetched from DB:", len(result_list))
        print("User IDs:", [u.id for u in result_list])

        # 🔁 LOOP ALL USERS (NO PAGINATION)
        for i in result_list:
            print("\n➡ Processing User ID:", i.id, "| Type:", i.user_type)

            obj = {}

            obj["doctor_id"] = i.id
            obj["doctor_name"] = i.name
            obj["profile_image"] = str(i.profile_image) if i.profile_image else ""
            obj["email"] = i.email
            obj["mobile_no"] = i.mobile_no
            obj["user_type"] = i.user_type
            obj['lat'] = i.latitude
            obj['long'] = i.longitude

            # ⭐ Rating
            ratings = UserRatingReview.objects.filter(
                fk_user_receiver__id=i.id
            ).values_list('rating', flat=True)

            obj["rating"] = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

            # ❤️ Favourite
            fav_exists = client_id and UserLike.objects.filter(
                fk_user_sender__id=client_id,
                fk_user_receiver__id=i.id
            ).exists()

            obj["added_fav"] = "True" if fav_exists else "False"

            # 📍 Distance
            distance_km = round(i.distance_km, 1) if hasattr(i, 'distance_km') else 0.0
            obj["distance_km"] = distance_km
            obj["distance"] = f"{distance_km} KM"

            print("   Distance:", obj["distance"])

            # 🧩 Availability
            avl = Set_Availability.objects.filter(fk_doctor__id=i.id).last()

            if not avl:
                print("❌ Availability NOT found for user", i.id, "→ SKIPPING USER")
                continue

            obj["from_shift"] = avl.from_shift
            obj["to_shift"] = avl.to_shift
            obj["select_days"] = ast.literal_eval(avl.select_days)

            # 🧑‍⚕️ Categorize
            if i.user_type == "Doctor":
                dr_lst.append(obj)

            elif i.user_type == "Trainer":
                trainer_lst.append(obj)

            elif i.user_type == "Sitter":
                sitter_lst.append(obj)

            elif i.user_type == "Walker":
                walker_lst.append(obj)

            elif i.user_type == "Salon":
                salon_lst.append(obj)

        print("\n================= API FINISHED =================\n")

        return Response({
            "status": 200,
            "msg": "Doctors List (50 KM radius)",
            "doctor": dr_lst,
            "trainer": trainer_lst,
            "sitter": sitter_lst,
            "walker": walker_lst,
            "salon": salon_lst
        })

    except Exception as e:
        print("\n❌ ERROR IN GET ALL DOCTORS LIST API")
        traceback.print_exc()

        return Response({
            "status": 403,
            "msg": "Something went wrong",
            "error": str(e)
        })


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_doctors_list_with_service_api(request):
    try:
        data = request.data
        page = data['page']
        fk_doctor = data['fk_doctor']
        list = []
        dict = {}
        if User_Details.objects.filter(id=fk_doctor).exists():
            obj = User_Details.objects.get(id=fk_doctor)
            max = int(page) * 10
            if page == "1":
                min = 0
            else:
                min = max - 10
            total_video = User_service.objects.filter(fk_doctor_id=fk_doctor).count()
            total_pages = str(round((total_video / 10) + 1))
            obj1 = User_service.objects.filter(fk_doctor_id=fk_doctor)[min:max]
            for i in obj1:
                dict['service_id'] = str(i.id) if i.id else ""
                dict['title'] = str(i.title) if i.title else ""
                dict['description'] = str(i.description) if i.description else ""
                dict['pet_type'] = str(i.pet_type) if i.pet_type else ""
                dict['charges'] = str(i.charges) if i.charges else ""
                list.append(dict)
                dict = {}
            return Response({'status': 200, "msg": "Doctors List with their services", "Doctor's name": obj.user_name,
                             "List": list, 'total_pages': str(total_pages)})
        else:
            return Response({'status': 403, "msg": 'Accounts not found'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['PATCH', 'POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def edit_userprofile_api(request):
    try:
        user_id = request.data.get('id')

        if not user_id:
            return Response(
                {"status": 400, "msg": "User id is required"},
                status=400
            )

        try:
            user_obj = User_Details.objects.get(id=user_id)
        except User_Details.DoesNotExist:
            return Response(
                {"status": 404, "msg": "User not found"},
                status=404
            )

        serializer = UserDetailSerializer1(
            user_obj,
            data=request.data,
            partial=True  # 🔥 THIS IS REQUIRED FOR PATCH
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": 200,
                    "msg": "Account updated successfully",
                    "payload": serializer.data
                }
            )

        return Response(
            {
                "status": 400,
                "msg": "Validation error",
                "errors": serializer.errors
            },
            status=400
        )

    except Exception as e:
        traceback.print_exc()
        return Response(
            {
                "status": 500,
                "msg": "Something went wrong",
                "error": str(e)
            },
            status=500
        )



@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def book_doctors_appointment_api(request):
    try:
        data = request.data
        doctor = User_Details.objects.get(id=data.get('doctor', None))
        client = User_Details.objects.get(id=data.get('client', None))
        fk_pet = New_Pet.objects.get(id=data.get('fk_pet', None))
        if not DoctorsAppointment.objects.filter(doctor=doctor,
                                                 booking_time=data['booking_time'],
                                                 booking_date=data['booking_date']).exclude(
            book_status='Cancelled').exists():
            serializer = DoctorsAppointmentSerializer(data=request.data,
                                                      context={'doctor': doctor, 'client': client, 'fk_pet': fk_pet})
            if serializer.is_valid():
                serializer.save()
                message_body = f'{client.name} has booked the appointment.'
                send_notification(message_body, doctor.token, 'Admin', 'Appointment Booked', doctor.id, 'Booking')
                return Response({'status': 200, "msg": 'Appointment booked successfully', 'payload': serializer.data})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": 403, "msg": "This slot is already booked"})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def doctors_appointment_list_api(request):
    try:
        id = request.data['id']
        user_type = request.data['user_type']
        if user_type == 'Doctor':
            obj = DoctorsAppointment.objects.filter(doctor__id=id).order_by('-id')
        else:
            obj = DoctorsAppointment.objects.filter(client__id=id,doctor__user_type = "Doctor").order_by('-id')
        # serializer = DoctorsAppointmentSerializer(obj, many=True)
        # user_ids = list(map(lambda a: a.id, obj))
        # user_obj = User_Details.objects.filter(id__in=user_ids)
        # serializer1 = UserDetailSerializer(user_obj, many=True)
        user_obj =  User_Details.objects.get(id =id) 
        lst = []
        data = {}
        for i in obj:
            data['appointment_id'] = str(i.id)
            data['doctor'] = str(i.doctor.id)
            data['client'] = str(i.client.id)
            data['client_name'] = str(i.client.name)
            data['fk_pet'] = str(i.fk_pet.id)
            data['pet_name'] = str(i.fk_pet.pet_name)
            data['type_of_pet'] = str(i.fk_pet.type_of_pet)
            data['breed'] = str(i.fk_pet.breed)
            data['pet_image'] = str(i.fk_pet.pet_image.url) if i.fk_pet.pet_image else ''
            data['booking_time'] = str(i.booking_time)
            data['booking_date'] = str(i.booking_date)
            data['amount'] = str(i.amount)
            data['services'] = str(i.services)
            data['book_status'] = str(i.book_status)
            data['doctor_name'] = str(i.doctor.name)
            data['bussiness_name'] = str(i.doctor.bussiness_name)
            data['latitude'] = str(i.doctor.latitude)
            data['longitude'] = str(i.doctor.longitude)
            data['bussiness_address'] = str(i.doctor.bussiness_address)
            data['doctor_profile_image'] = str(i.doctor.profile_image.url) if i.doctor.profile_image else ''
            rating_lst = list(
                map(lambda a: a.rating, UserRatingReview.objects.filter(fk_user_receiver__id=i.doctor.id)))
            count = UserRatingReview.objects.filter(fk_user_receiver__id=i.doctor.id).count()
            if count != 0:
                data['total_rating'] = sum(rating_lst) / count
            else:
                data['total_rating'] = 0.0
            if UserRatingReview.objects.filter(fk_apt_id = i.id , fk_user_sender = user_obj).exists() :
                rating_obj = UserRatingReview.objects.get(fk_apt_id = i.id , fk_user_sender = user_obj)
                data['rating'] = rating_obj.rating
                data['review'] = rating_obj.comment
            else: 
                data['rating']  = 0
                data['review'] = ""
            lst.append(data)
            data = {}
        return Response({'status': 200, "msg": 'Doctor\'s Appointment List', 'payload': lst})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def like_user_api(request):
    try:
        data = request.data
        if UserLike.objects.filter(fk_user_sender__id=data['fk_user_sender'],fk_user_receiver__id=data['fk_user_receiver']).exists():
            UserLike.objects.filter(fk_user_sender__id=data['fk_user_sender'],fk_user_receiver__id=data['fk_user_receiver']).delete()
            return Response({'status': 200, "msg": 'You disliked the user.'})
        
        else:
            sender_obj = User_Details.objects.filter(id = data['fk_user_sender'])[0]
            receiver_obj = User_Details.objects.filter(id = data['fk_user_receiver'])[0]
            UserLike.objects.create(fk_user_sender=sender_obj,fk_user_receiver=receiver_obj,status = True,date = data['date'])
            obj = UserLike.objects.filter(fk_user_sender=sender_obj,fk_user_receiver=receiver_obj).values()
            return Response({'status': 200, "msg": 'You liked the user.', 'payload': obj[0]})
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def user_rating_api(request):
    try:
        data = request.data
        
        # if UserRatingReview.objects.filter(fk_user_sender__id=data['fk_user_sender'],
        #                                    fk_user_receiver__id=data['fk_user_receiver']).exists():
        #     obj = UserRatingReview.objects.get(fk_user_sender__id=data['fk_user_sender'],
        #                                        fk_user_receiver__id=data['fk_user_receiver'])
        #     serializer = UserRatingReviewSerializer(obj, data=data)
        # else:
        serializer = UserRatingReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            DoctorsAppointment.objects.filter(id = data['fk_apt']).update(review_status = True)
            return Response({'status': 200, "msg": 'User rating updated.', 'payload': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def cancel_doctors_appointment_api(request):
    try:
        data = request.data
        appointment_id = data.get('id')
        cancelled_by = data.get('cancelled_by')

        if not appointment_id or not cancelled_by:
            return Response({"status": 400, "msg": "Missing required fields"})

        if not DoctorsAppointment.objects.filter(id=appointment_id).exists():
            return Response({"status": 404, "msg": "Appointment not found"})

        obj = DoctorsAppointment.objects.get(id=appointment_id)

        serializer = DoctorsAppointmentSerializer(obj, data=data, partial=True)
        if not serializer.is_valid():
            return Response({"status": 400, "msg": serializer.errors})

        serializer.save()

        # Decide sender and receiver dynamically
        cancelled_by_lower = cancelled_by.lower()

        if cancelled_by_lower == "customer":
            sender_name = obj.client.name
            sender_role = "Customer"
            receiver_token = obj.doctor.token
            receiver_id = obj.doctor.id

        else:
            sender_name = obj.doctor.name
            sender_role = cancelled_by
            receiver_token = obj.client.token
            receiver_id = obj.client.id

        message_body = f"{sender_name} has cancelled the appointment."

        send_notification(
            message_body=message_body,
            token=receiver_token,
            sender=sender_role,
            notification_title="Appointment Cancelled",
            uid=receiver_id,
            type="Cancelled"
        )

        return Response({
            'status': 200,
            "msg": "Appointment cancelled successfully",
            'payload': serializer.data
        })

    except Exception as e:
        print(str(traceback.format_exc()))
        return Response({
            "status": 500,
            "msg": "Something went wrong",
            "error": str(e)
        })



@api_view(['PUT'])
@permission_classes((AllowAny,))
@csrf_exempt
def update_doctors_appointment_api(request):
    try:
        data = request.data
        obj = DoctorsAppointment.objects.get(id=data['id'])
        serializer = DoctorsAppointmentSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 200, "msg": 'Appointment updated successfully', 'payload': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def show_doctors_data_api(request):
    try:
        data = request.data
        doc_id = data['doc_id']
        cust_id = data['cust_id']
        current_lat = data['current_lat']
        current_long = data['current_long']

        user_obj = User_Details.objects.get(id=doc_id)
        srvc_obj = User_service.objects.filter(fk_doctor__id=doc_id).values()
        rating_obj = UserRatingReview.objects.filter(fk_user_receiver__id=doc_id)
        serializer1 = UserDetailSerializer(user_obj)
        serializer2 = DoctorServiceSerializer(srvc_obj, many=True)
        rating_lst = list(map(lambda a: a.rating, rating_obj))
        if len(rating_lst) == 0:
            avg_rating = 0.0
        else:
            avg_rating = sum(rating_lst) / len(rating_lst)
        R = 6373.0
        dict = {}
        data = {}
        try:
            lat1 = radians(float(current_lat))
            lon1 = radians(float(current_long))
            lat2 = radians(float(user_obj.latitude))
            lon2 = radians(float(user_obj.longitude))

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c
            distance_in_km = round(distance, 1)
            dict["distance"] = str(distance_in_km) + " KM"
        except:
            print(str(traceback.format_exc()))
            dict["distance"] = "0.0 km"
        
        
        data = serializer1.data
        # print(serializer1.data.get('profile_image')[6:])
        # print(user_obj.profile_image)
        profile_image = serializer1.data.get('profile_image')
        data['profile_image'] = profile_image[7:] if profile_image else ""
        data['avg_rating'] = str(avg_rating)[0:3]              
        data['distance'] = dict['distance']
        data['services'] = serializer2.data
        data['added_fav'] = "True" if UserLike.objects.filter(fk_user_receiver__id=doc_id,
                                                       fk_user_sender__id=cust_id).exists() else "False"
        avl_obj = Set_Availability.objects.filter(fk_doctor__id=doc_id)
        lst = []
        dict = {}
        for i in avl_obj:
            dict['add_shift'] = str(i.add_shift)
            dict['from_shift'] = str(i.from_shift)
            dict['to_shift'] = str(i.to_shift)
            dict['select_days'] = ast.literal_eval(i.select_days) if i.select_days else []
            lst.append(dict)
            dict = {}
        data['availability'] = lst
        
        return Response({'status': 200, "msg": 'Doctor\'s Data', 'payload': data})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_user_profile_api(request):
    try:
        data = request.data
        if User_Details.objects.filter(id=data['id']).exists():
            user_obj = User_Details.objects.get(id=data['id'])
            pro_image = str(user_obj.profile_image.url) if user_obj.profile_image else ""
            return Response(
                {'status': 200, "msg": 'User details', "user_id": user_obj.id, 
                 "name": user_obj.name, "email": user_obj.email, "mobile_no": user_obj.mobile_no,
                 "address": user_obj.address, "map_location": user_obj.map_location,
                 "latitude": user_obj.latitude, "longitude": user_obj.longitude, "about_me": user_obj.about_me,
                 "country_code": user_obj.country_code, 'pro_image': pro_image,
                 'bussiness_name': user_obj.bussiness_name,
                 'bussiness_address': user_obj.bussiness_address,"user_type": user_obj.user_type,'profile_created':str(user_obj.is_profile_create)})
        else:
            return Response({'status': 403, "msg": 'Invalid Credential'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_last_visited_doctors_list(request):
    try:
        data = request.data

        user_id = data.get('user_id')
        current_lat = data.get('current_lat')
        current_long = data.get('current_long')
        page = int(data.get('page', 1))

        lst = []
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page

        R = 6373.0  # Earth radius

        if not DoctorsAppointment.objects.filter(client__id=user_id).exists():
            return Response({'status': 403, "msg": 'No Data'})

        today = datetime.today().date()

        # ✅ FIX 1: ONLY past appointments
        appointments = DoctorsAppointment.objects.filter(
            client__id=user_id,
            booking_date__lt=today
        )

        if not appointments.exists():
            return Response({'status': 403, "msg": 'No Data'})

        # ✅ FIX 2: UNIQUE doctor IDs
        doctor_ids = list(
            appointments.values_list('doctor__id', flat=True).distinct()
        )

        total = len(doctor_ids)
        total_pages = str((total // per_page) + 1)

        doctors = User_Details.objects.filter(id__in=doctor_ids)[start:end]

        for i in doctors:
            obj = {}

            obj['doctor_id'] = i.id
            obj['doctor_name'] = i.name
            obj['profile_image'] = str(i.profile_image) if i.profile_image else ""
            obj['email'] = i.email
            obj['mobile_no'] = i.mobile_no
            obj['user_type'] = i.user_type

            # Availability
            avl_obj = Set_Availability.objects.filter(fk_doctor__id=i.id).last()
            obj['from_shift'] = avl_obj.from_shift if avl_obj else ''
            obj['to_shift'] = avl_obj.to_shift if avl_obj else ''
            obj['select_days'] = ast.literal_eval(avl_obj.select_days) if avl_obj else []

            obj['lat'] = i.latitude
            obj['long'] = i.longitude

            # Rating
            ratings = UserRatingReview.objects.filter(
                fk_user_receiver__id=i.id
            ).values_list('rating', flat=True)

            obj['rating'] = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

            # Favourite
            obj['added_fav'] = "True" if UserLike.objects.filter(
                fk_user_sender__id=user_id,
                fk_user_receiver__id=i.id
            ).exists() else "False"

            # ✅ FIX 3: Distance calculation safe
            try:
                if current_lat and current_long:
                    lat1 = radians(float(current_lat))
                    lon1 = radians(float(current_long))
                    lat2 = radians(float(i.latitude))
                    lon2 = radians(float(i.longitude))

                    dlon = lon2 - lon1
                    dlat = lat2 - lat1

                    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                    c = 2 * atan2(sqrt(a), sqrt(1 - a))

                    distance_km = round(R * c, 1)
                    obj["distance"] = f"{distance_km} KM"
                else:
                    obj["distance"] = "0.0 KM"
            except:
                obj["distance"] = "0.0 KM"

            lst.append(obj)

        return Response({
            'status': 200,
            "msg": "Doctors List",
            "List": lst,
            "total_pages": total_pages
        })

    except Exception as e:
        return Response({
            "status": 403,
            "msg": "Something went wrong",
            "error": str(e)
        })



@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def doctors_appointment_detail_api(request):
    try:
        data = request.data
        id = data['id']
        obj = DoctorsAppointment.objects.get(id=id)
        services = obj.services.split(',')
        serializer = DoctorsAppointmentSerializer(obj)
        payload = serializer.data
        srvc_obj = User_service.objects.get(id=services[0])
        payload['services'] = DoctorServiceSerializer(srvc_obj).data
        return Response({'status': 200, "msg": "Doctors appointment details", 'payload': payload})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def show_notification_list_api(request):
    try:
        data = request.data
        obj = Notification.objects.filter(receiver__id=data['user_id']).order_by('-id')
        serializer = NotificationSerializer(obj, many=True)
        return Response({'status': 200, "msg": "Doctors appointment details", 'payload': serializer.data})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def del_notification_api(request):
    try:
        data = request.data
        Notification.objects.filter(id=data['id']).delete()
        return Response({'status': 200, "msg": "Notification deleted"})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def customer_home_api(request):
    try:
        data = request.data
        customer_id = data['customer_id']
        cust_obj = New_Pet.objects.filter(fk_customer__id=customer_id)
        serializer = AddNewPetSerializer(cust_obj)
        return Response({'status': 200, "msg": "Doctors appointment details", 'payload': serializer.data})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# @csrf_exempt
# def forgot_password_api(request):
#     print("---- FORGOT PASSWORD API HIT ----")

#     try:
#         print("Raw request data:", request.data)
#         data = request.data

#         if 'email' not in data:
#             print("ERROR: Email key missing in request")
#             return Response({'status': 400, 'msg': 'Email is required'})

#         print("Checking if user exists for email:", data['email'])

#         if User_Details.objects.filter(email=data['email']).exists():
#             print("User exists")

#             user_obj = User_Details.objects.get(email=data['email'])
#             print("User fetched:", user_obj.id, user_obj.email)

#             print("Calling forgot_password_email()")
#             new_password = forgot_password_email(user_obj.name, user_obj.email)
#             print("New password generated:", new_password)

#             user_obj.password = new_password
#             user_obj.save()
#             print("Password saved successfully")

#             return Response({
#                 'status': 200,
#                 'msg': 'New password has been sent to your registered email.'
#             })

#         else:
#             print("User does NOT exist for email:", data['email'])
#             return Response({'status': 403, 'msg': 'Email does not exists..!'})


#     except Exception as e:
#         print("---- EXCEPTION IN forgot_password_api ----")
#         print(str(e))
#         print(traceback.format_exc())

#         return Response({
#             'status': 403,
#             'msg': 'Something went wrong',
#             'error': str(e)
#         })
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import traceback

@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def forgot_password_api(request):
    print("---- FORGOT PASSWORD API HIT ----")

    try:
        print("Raw request data:", request.data)
        data = request.data

        if 'email' not in data:
            print("ERROR: Email key missing in request")
            return Response({'status': 400, 'msg': 'Email is required'})

        print("Checking if user exists for email:", data['email'])

        if User_Details.objects.filter(email=data['email']).exists():
            print("User exists")

            user_obj = User_Details.objects.get(email=data['email'])
            print("User fetched:", user_obj.id, user_obj.email)

            # Set static password
            new_password = "123456"
            user_obj.password = new_password
            user_obj.save()

            print("Password reset to 123456 successfully")

            return Response({
                'status': 200,
                'msg': 'Password has been reset successfully.'
            })

        else:
            print("User does NOT exist for email:", data['email'])
            return Response({
                'status': 403,
                'msg': 'Email does not exist'
            })

    except Exception as e:
        print("---- EXCEPTION IN forgot_password_api ----")
        print(str(e))
        print(traceback.format_exc())

        return Response({
            'status': 403,
            'msg': 'Something went wrong',
            'error': str(e)
        })


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def change_password_api(request):
    try:
        data = request.data
        id = data['id']
        old_password = data['old_password']
        new_password = data['new_password']
        if User_Details.objects.filter(id=id, password=old_password).exists():
            user_obj = User_Details.objects.get(id=id)
            user_obj.password = new_password
            user_obj.save()
            return Response({'status': 200, "msg": "Your password has been updated."})
        else:
            return Response({'status': 403, "msg": "Password does not match..!"})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})



@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def Check_User(request):
    try:
        data = request.data
        if data['email'] == "":
            print("1")
            if User_Details.objects.filter( mobile_no = data['mobile_no'] , user_type = data['user_type']).exists():
                return Response({'status': 403, "msg": "Mobile Number already exists."})
            else:
                return Response({'status': 200, "msg": "Success."})
        elif data['mobile_no'] == "":
            print("2")
            if User_Details.objects.filter(email = data['email'] ,  user_type = data['user_type']).exists():
                return Response({'status': 403, "msg": "Email ID already exists."})
            else:
                return Response({'status': 200, "msg": "Success."})
        else:
            print("3")
            if User_Details.objects.filter(email = data['email'] , user_type = data['user_type']).exists():
                return Response({'status': 403, "msg": "Email ID already exists."})
            elif User_Details.objects.filter(mobile_no = data['mobile_no'] , user_type = data['user_type']).exists():
                return Response({'status': 403, "msg": "Mobile Number already exists."})
            else:
                return Response({'status': 200, "msg": "Success."})
    except:
        
        return Response({"status": 403, "msg": "Something went wrong."})



############################# API ############################

@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_bookings(request):
    try:
        data = request.data
        user_id = data.get("user_id")
        user_obj = User_Details.objects.get(id=user_id)

        temp = ['Sitter', 'Trainer', 'Walker', 'Salon']

        # Role based query
        if user_obj.user_type == "Customer":
            bookings = DoctorsAppointment.objects.filter(
                client=user_obj,
                doctor__user_type__in=temp
            ).values().order_by('-id')

        else:  # Vendor / Doctor
            bookings = DoctorsAppointment.objects.filter(
                doctor=user_obj
            ).values().order_by('-id')

        for i in bookings:
            obj = User_Details.objects.get(id=i['doctor_id'])

            i['doctor_name'] = obj.name
            i['profile'] = f"{settings.IMAGE_BASE_URL}{obj.profile_image}" if obj.profile_image else ''

            rating_qs = UserRatingReview.objects.filter(fk_user_receiver__id=i['doctor_id'])
            count = rating_qs.count()

            if count:
                i['total_rating'] = sum(r.rating for r in rating_qs) / count
            else:
                i['total_rating'] = 0.0

            if UserRatingReview.objects.filter(fk_apt_id=i['id'], fk_user_sender=user_obj).exists():
                rating_obj = UserRatingReview.objects.get(fk_apt_id=i['id'], fk_user_sender=user_obj)
                i['rating'] = rating_obj.rating
                i['review'] = rating_obj.comment
            else:
                i['rating'] = 0
                i['review'] = ""

            # 🔥 ADD PET OBJECT HERE
            if i['fk_pet_id']:
                pet = New_Pet.objects.get(id=i['fk_pet_id'])

                i['pet'] = {
                    "id": pet.id,
                    "pet_name": pet.pet_name,
                    "type_of_pet": pet.type_of_pet,
                    "breed": pet.breed,
                    "age": pet.age,
                    "pet_image": f"{settings.IMAGE_BASE_URL}{pet.pet_image}" if pet.pet_image else ""
                }
            else:
                i['pet'] = None

            # 🔥 ADD PET OBJECT HERE
            if i['client_id']:
                client = User_Details.objects.get(id=i['client_id'])

                i['client'] = {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "mobile_no": client.mobile_no,
                    "map_location": client.map_location,
                    "address": client.address,
                    "latitude": client.latitude,
                    "longitude": client.longitude,
                    "profile_image": f"{settings.IMAGE_BASE_URL}{client.profile_image}" if client.profile_image else ""
                }
            else:
                i['client'] = None

        return JsonResponse({"status": 200, "bookings": list(bookings)})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"status": 403, "msg": "Something Went Wrong"})

   
@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def cancel_booking(request):
    try :
        data = request.data
        booking_id = data.get("booking_id")  
        cancelled_by = data.get("cancelled_by") 
        booking_obj = DoctorsAppointment.objects.get(id =booking_id)  
        booking_obj.cancelled_by = cancelled_by
        booking_obj.book_status = "Cancelled"
        booking_obj.save() 
        return JsonResponse({"status":200,'msg':"Booking Cancelled Successfully"})
    except:
        traceback.print_exc()
        return JsonResponse({"Status":403,"msg":"Something Went Wrong"})
  

   
@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def cancel_order_api(request):
    try :
        data = request.data
        order_id = data.get("order_id")  
        cancelled_by = data.get("cancelled_by") 
        cancelled_reason = data.get("cancelled_reason") 
        order_obj = OrdersTable.objects.get(id = order_id)  
        order_obj.order_status = "Cancelled"
        order_obj.cancelled_by = cancelled_by
        order_obj.cancelled_reason = cancelled_reason
        order_obj.save() 
        message_body = f'#{order_obj.order_no} has been cancelled.'
        send_notification(message_body, order_obj.fk_users.token, 'Admin', 'Order Cancelled', order_obj.fk_users.id, 'Order')
        return JsonResponse({"status":200,'msg':"Order Cancelled Successfully"})
    except:
        traceback.print_exc()
        return JsonResponse({"Status":403,"msg":"Something Went Wrong"})
  

   
@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def billing_history_api(request):
    try :
        data = request.data
        user_id = data.get("user_id")  
        payload = []    
        user_obj = User_Details.objects.get(id =user_id)  
        payload = DoctorsAppointment.objects.filter(client = user_obj,book_status = "Completed").values().order_by("-id")
        for i in payload : 
            obj = User_Details.objects.get(id=i['doctor_id'])
            i['vender_name'] = obj.name
            i['vender_image'] =  f"{settings.IMAGE_BASE_URL}{obj.profile_image}" if obj.profile_image else ''
        return JsonResponse({"status":200, "payload":list(payload)})
    except:
        traceback.print_exc()
        return JsonResponse({"Status":403,"msg":"Something Went Wrong"})
  

  
@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def order_history_api(request):
    try :
        data = request.data
        user_id = data.get("user_id")   
        user_obj = User_Details.objects.get(id =user_id)  
        order_obj = OrdersTable.objects.filter(fk_users = user_obj).values()
        for i in order_obj :  
            item_obj = OrderItemTable.objects.filter(fk_orders_id = i['id']).values()
            for j in item_obj :
                obj = StoreProduct.objects.get(id = j['fk_item_id'])
                j["item_name"] =  f"{obj.item_name}" 
                j["item_image"] =  f"{obj.item_image}" 
            i["item_list"] = list(item_obj)
        return JsonResponse({"status":200, "payload":list(order_obj)})
    except:
        traceback.print_exc()
        return JsonResponse({"Status":403,"msg":"Something Went Wrong"})
   

@api_view(['GET'])
@permission_classes((AllowAny,))
@csrf_exempt  
def get_item_list_api(request):
    try :
        items = StoreProduct.objects.filter(available_status = True).values().order_by('-id')   
        for i in items:
            rating_lst = list(map(lambda a: a.rating, UserRatingReview.objects.filter(fk_user_receiver__id=i['fk_vendor_id'])))
            count = UserRatingReview.objects.filter(fk_user_receiver__id=i['fk_vendor_id']).count()
            i['vender_name'] = User_Details.objects.get(id = i['fk_vendor_id']).name
            i['vender_latitute'] = User_Details.objects.get(id = i['fk_vendor_id']).latitude
            i['vender_longitude'] = User_Details.objects.get(id = i['fk_vendor_id']).longitude
            i['vender_address'] = User_Details.objects.get(id = i['fk_vendor_id']).map_location
            i['category_name'] = ItemCategoryMaster.objects.get(id = i['fk_category_id']).category_name 
            if count != 0:
                i['rating'] = sum(rating_lst) / count 
            else:
                i['rating'] = 0.0   
            print(i,'==========')    
        item =(sorted(items, key=lambda x: x['rating'] ,reverse = True))  
        return JsonResponse({"status":200,'payload': list(item) })
    except :
        traceback.print_exc()
        return JsonResponse({"Status":403,"msg":"Something Went Wrong"})
        
@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt  
def show_cart_items_api(request):
    try :
        data = request.data
        user_id = data.get("user_id")    
        user_obj = User_Details.objects.get(id = user_id)  
        items = AddtoCart.objects.filter(fk_user = user_obj).values()
        for j in items :
            obj = StoreProduct.objects.get(id = j['fk_item_id'])
            j["item_name"] =  obj.item_name
            j["item_image"] =  f"{obj.item_image}"
            j["item_price"] =  obj.item_price
            j["pet_type"] =  obj.pet_type
            j["fk_category"] = obj.fk_category.category_name          
        return JsonResponse({"status":200, "payload":list(items)})
    except:
        traceback.print_exc()
        return JsonResponse({"Status":403,"msg":"Something Went Wrong"})
        
        
@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def place_order_api(request):
    try:
        data = request.data

        # ---------- BASIC VALIDATION ----------
        customer_id = data.get('customer_id')
        items = data.get('items')

        if not customer_id or not items:
            return JsonResponse({'status': 0, 'msg': 'Missing required fields'})

        user_obj = User_Details.objects.get(id=customer_id)

        # ---------- ADDRESS ----------
        deliveryAddress.objects.update_or_create(
            fk_users=user_obj,
            defaults={
                "name": data.get('name'),
                "email": data.get('email'),
                "address1": data.get('address1'),
                "address2": data.get('address2'),
                "country_code": data.get('country_code'),
                "mobile_no": data.get('mobile'),
                "province": data.get('province_name'),
                "city": data.get('city_name'),
                "postalcode": data.get('postal_code'),
                "country": data.get('country_name'),
            }
        )

        booking_time = datetime.now().time()
        booking_date = datetime.now().date()

        items = yaml.safe_load(items)  # expected list of dicts

        # ---------- ORDER CREATION ----------
        with transaction.atomic():

            order_no = "OID" + str(random.randint(100000, 999999))
            while OrdersTable.objects.filter(order_no=order_no).exists():
                order_no = "OID" + str(random.randint(100000, 999999))

            order_obj = OrdersTable.objects.create(
                order_no=order_no,
                fk_users=user_obj,
                booking_time=booking_time,
                booking_date=booking_date,
                order_status="Pending",
                delivery_note=data.get('note'),
                status=True,
                name=data.get('name'),
                email=data.get('email'),
                address1=data.get('address1'),
                address2=data.get('address2'),
                country_code=data.get('country_code'),
                mobile_no=data.get('mobile'),
                province=data.get('province_name'),
                city=data.get('city_name'),
                postalcode=data.get('postal_code'),
                country=data.get('country_name'),
            )

            subtotal = 0
            total_quantity = 0
            vendor = None

            for i in items:
                item_obj = StoreProduct.objects.select_related('fk_vendor').get(
                    id=i['item_id']
                )

                vendor = item_obj.fk_vendor  # ✅ CORRECT FK

                item_total_price = float(i['quantity']) * float(item_obj.item_price)

                OrderItemTable.objects.create(
                    fk_orders=order_obj,
                    fk_item=item_obj,
                    fk_vendors=vendor,     # ✅ USER_Details object
                    item_quantity=i['quantity'],
                    item_price=item_obj.item_price,
                    item_total_price=item_total_price,
                )

                subtotal += item_total_price
                total_quantity += int(i['quantity'])

            delivery_charge = float(data.get('delivery_charge', 0))
            convenience_fee = float(data.get('convinience_fee', 0))

            order_obj.item_price = subtotal
            order_obj.total_quantity = total_quantity
            order_obj.delivery_charge = delivery_charge
            order_obj.taxes = convenience_fee
            order_obj.total_amount = subtotal + delivery_charge + convenience_fee
            order_obj.fk_business = vendor
            order_obj.save()

            # ---------- CLEAR CART ----------
            AddtoCart.objects.filter(fk_user=user_obj).delete()

        return JsonResponse({'status': '1', 'msg': 'Order placed successfully'})

    except User_Details.DoesNotExist:
        return JsonResponse({'status': '0', 'msg': 'Invalid customer'})
    except StoreProduct.DoesNotExist:
        return JsonResponse({'status': '0', 'msg': 'Invalid item in cart'})
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': '0', 'msg': 'Something went wrong'})

          
# items = [
#     {
#     'item_id': 2,
#     'quantity': 4,
#     'total_amount': 220,
#     },
#     {
#     'item_id': 2,   
#     'quantity': 4,
#     'total_amount': 220,
#     },
# ]


@api_view(['POST'])
@permission_classes((AllowAny,))     
@csrf_exempt
def get_delivery_address_api(request):
    try:
        data = request.data 
        user_id = data.get('user_id')
       
        if deliveryAddress.objects.filter(fk_users_id = user_id).exists():
            obj = deliveryAddress.objects.get(fk_users_id = user_id)
            data = {
                "fk_users": obj.name,
                "user_name": "",
                "mobile_no": obj.mobile_no,
                "country": obj.country,
                "country_code": obj.country_code,
                "email": obj.email ,
                "address1": obj.address1,
                "address2": obj.address2,
                "province": obj.province,
                "city": obj.city,
                "postalcode": obj.postalcode,
                "name" : "",
                "about_me" : "",
                "bussiness_name" : "",
                "bussiness_address" : "",
                "map_location" : "",
                "latitude" : "",
                "longitude" : "",
                "address" : "",
                "profile_image" : "",
                "user_type" : "",
                "status" : "",
                "created_datetime" : "",
                "sign_up_status" : "",
                "is_profile_create" : "",
                "token" : "",
            }   
        else : 
            obj = User_Details.objects.get(id=user_id)
            data = {
                "fk_users": obj.name,
                "user_name": obj.user_name,
                "mobile_no": obj.mobile_no,
                "country": obj.country,
                "country_code": obj.country_code,
                "email": obj.email ,
                "address1": "",
                "address2": "",
                "province": "",
                "city": "",
                "postalcode": "",
                "name" : obj.name,
                "about_me" : obj.about_me,
                "bussiness_name" : obj.bussiness_name,
                "bussiness_address" : obj.bussiness_address,
                "map_location" : obj.map_location,
                "latitude" : obj.latitude,
                "longitude" : obj.longitude,
                "address" : obj.address,
                "profile_image" : "",
                "user_type" : obj.user_type,
                "status" : obj.status,
                "created_datetime" : obj.created_datetime,
                "sign_up_status" : obj.sign_up_status,
                "is_profile_create" : obj.is_profile_create,
                "token" : obj.token,
            } 
        return JsonResponse({'status':'1' , 'data': data})
    except:
        traceback.print_exc()
        return JsonResponse({'status':'0','msg':'Something went wrong.'})

        
@api_view(['POST'])
@permission_classes((AllowAny,))     
@csrf_exempt        
def get_state_of_country_api(request):
    try:
        county_obj = CountryMaster.objects.all().values()
        serializer = countrySerializer(county_obj,  many=True)
        return JsonResponse({'status': '1',"data": serializer.data})
    except:
        print(traceback.print_exc())
        return JsonResponse({'status':'0','msg':'Something went wrong.'})


@api_view(['POST'])
@permission_classes((AllowAny,))     
@csrf_exempt 
def get_province_api(request):
    try:
        data = request.data 
        country_id = data.get('country_id')
        country_obj = CountryMaster.objects.filter(id = country_id)[0]
        province_obj = ProvinceMaster.objects.filter(country_id = country_id).values()
        serializer = provinceSerializer(province_obj,  many=True)        
        return JsonResponse({'status': '1','data':serializer.data})
    except:
        print(traceback.print_exc())
        return JsonResponse({'status':'0','msg':'Something went wrong.'})


@api_view(['POST'])
@permission_classes((AllowAny,))     
@csrf_exempt 
def get_city_api(request):
    try:
        data = request.data 
        province_id = data.get('province_id')
        province_obj = ProvinceMaster.objects.filter(id = province_id)
        city_obj = CityMaster.objects.filter(state_id = province_id).values()
        serializer = citySerializer(city_obj,  many=True)
        return JsonResponse({'status': '1','data':serializer.data})
    except:
        print(traceback.print_exc())
        return JsonResponse({'status':'0','msg':'Something went wrong.'})


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def get_pet_type(request):
    pets = PetMaster.objects.all()

    if not pets.exists():
        JsonResponse({'status':'0','msg':'Something went wrong.'})

    serializer = PetMasterSerializer(pets, many=True)
    return JsonResponse({'status': '1',
        "message": "Pet type fetched successfully",
        "data": serializer.data})



@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def get_item_category(request):
    cat = ItemCategoryMaster.objects.all()

    if not cat.exists():
        JsonResponse({'status':'0','msg':'No Items available.'})

    serializer = ItemCatMasterSerializer(cat, many=True)
    return JsonResponse({'status': '1',
        "message": "Category fetched successfully",
        "data": serializer.data})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def store_orders_list_api(request):
    try:
        data = request.data
        store_id = data.get('store_id')

        if not store_id:
            return JsonResponse({'status': '0', 'msg': 'store_id is required'})

        store_obj = User_Details.objects.get(id=store_id)


        accepted_orders_qs = OrdersTable.objects.filter(fk_business=store_obj,order_status="Approved").values()
        for i in accepted_orders_qs :  
            item_obj = OrderItemTable.objects.filter(fk_orders_id = i['id']).values()
            for j in item_obj :
                obj = StoreProduct.objects.get(id = j['fk_item_id'])
                j["item_name"] =  f"{obj.item_name}" 
                j["item_image"] =  f"{obj.item_image}" 
            i["item_list"] = list(item_obj)


        received_orders_qs = OrdersTable.objects.filter(fk_business=store_obj,order_status="Pending").values()
        for i in received_orders_qs :  
            item_obj = OrderItemTable.objects.filter(fk_orders_id = i['id']).values()
            for j in item_obj :
                obj = StoreProduct.objects.get(id = j['fk_item_id'])
                j["item_name"] =  f"{obj.item_name}" 
                j["item_image"] =  f"{obj.item_image}" 
            i["item_list"] = list(item_obj)


        return JsonResponse({
            'status': '1',
            'received_orders': list(received_orders_qs),
            'accepted_orders': list(accepted_orders_qs)
        })

    except User_Details.DoesNotExist:
        return JsonResponse({'status': '0', 'msg': 'Invalid store'})
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': '0', 'msg': 'Something went wrong'})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def store_past_orders_api(request):
    try:
        data = request.data
        store_id = data.get('store_id')
        from_date = data.get('from_date')   # format: YYYY-MM-DD
        to_date = data.get('to_date')       # format: YYYY-MM-DD

        if not store_id:
            return JsonResponse({'status': '0', 'msg': 'store_id is required'})

        store_obj = User_Details.objects.get(id=store_id)

        orders_qs = OrdersTable.objects.filter(
            fk_business=store_obj
        ).exclude(order_status="Pending").order_by('-id').values()

        # ---------- DATE FILTER ----------
        if from_date and to_date:
            orders_qs = orders_qs.filter(
                booking_date__range=[from_date, to_date]
            ).values()

        for i in orders_qs :  
            item_obj = OrderItemTable.objects.filter(fk_orders_id = i['id']).values()
            for j in item_obj :
                obj = StoreProduct.objects.get(id = j['fk_item_id'])
                j["item_name"] =  f"{obj.item_name}" 
                j["item_image"] =  f"{obj.item_image}" 
            i["item_list"] = list(item_obj)

        return JsonResponse({
            'status': '1',
            'past_orders': list(orders_qs)
        })

    except User_Details.DoesNotExist:
        return JsonResponse({'status': '0', 'msg': 'Invalid store'})
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': '0', 'msg': 'Something went wrong'})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def store_add_item_api(request):
    try:
        data = request.data

        title = data['title']
        item_category_id = data['item_type']
        pet_type = data.get('pet_type')
        description = data.get('description')
        charges = data['charges']
        available = data.get('available', True)
        user_id = data['user_id']
        item_image = data.get('item_image')   # base64 string

        category_obj = ItemCategoryMaster.objects.get(id=item_category_id)
        vendor_obj = User_Details.objects.get(id=user_id)

        # ---------- IMAGE UPLOAD ----------
        if item_image:
            uploaded_image = upload_image(item_image, "item_image/", "item_")
        else:
            uploaded_image = ""

        if str(available).lower() == "true":
            available = True
        else:
            available = False

        # ---------- CREATE ITEM ----------
        obj = StoreProduct.objects.create(
            fk_vendor=vendor_obj,
            fk_category=category_obj,
            item_name=title,
            item_price=charges,
            item_image=uploaded_image,
            pet_type=pet_type,
            item_description=description,
            available_status=available
        )

        return Response({
            'status': '1',
            "msg": "Item Added Successfully",
            "item_id": obj.id
        })

    except ItemCategoryMaster.DoesNotExist:
        return Response({"status": '0', "msg": "Invalid category"})
    except User_Details.DoesNotExist:
        return Response({"status": '0', "msg": "Invalid vendor"})
    except:
        print(str(traceback.format_exc()))
        return Response({
            "status": '0',
            "msg": "Something went wrong",
            "error": str(traceback.format_exc())
        })


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_all_items_api(request):
    try:
        data = request.data

        vendor_id = data.get('user_id')          # optional
        category_id = data.get('item_type')      # optional
        pet_type = data.get('pet_type')          # optional
        available = data.get('available')        # optional (true/false)

        qs = StoreProduct.objects.all().order_by('-id')

        # ---------- FILTERS ----------
        if vendor_id:
            qs = qs.filter(fk_vendor__id=vendor_id)

        if category_id:
            qs = qs.filter(fk_category__id=category_id)

        if pet_type:
            qs = qs.filter(pet_type=pet_type)

        if available is not None:
            if str(available).lower() == "true":
                qs = qs.filter(available_status=True)
            else:
                qs = qs.filter(available_status=False)

        item_list = []

        for i in qs:
            item_list.append({
                "item_id": i.id,
                "title": i.item_name,
                "charges": i.item_price,
                "pet_type": i.pet_type,
                "description": i.item_description,
                "available": i.available_status,
                "category_id": i.fk_category.id if i.fk_category else None,
                "category_name": i.fk_category.category_name if i.fk_category else "",
                "vendor_id": i.fk_vendor.id if i.fk_vendor else None,
                "vendor_name": i.fk_vendor.name if i.fk_vendor else "",
                "item_image": f"{settings.IMAGE_BASE_URL}{i.item_image}" if i.item_image else ""
            })

        return Response({
            "status": "1",
            "msg": "Item List",
            "items": item_list
        })

    except Exception as e:
        print(str(traceback.format_exc()))
        return Response({
            "status": "0",
            "msg": "Something went wrong",
            "error": str(e)
        })


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def store_update_item_api(request):
    try:
        data = request.data

        item_id = data['item_id']
        title = data.get('title')
        item_category_id = data.get('item_type')
        pet_type = data.get('pet_type')
        description = data.get('description')
        charges = data.get('charges')
        available = data.get('available')
        item_image = data.get('item_image')   # base64 or empty

        item_obj = StoreProduct.objects.get(id=item_id)

        # ---------- UPDATE FIELDS ----------
        if title:
            item_obj.item_name = title

        if item_category_id:
            category_obj = ItemCategoryMaster.objects.get(id=item_category_id)
            item_obj.fk_category = category_obj

        if pet_type:
            item_obj.pet_type = pet_type

        if description:
            item_obj.item_description = description

        if charges:
            item_obj.item_price = charges

        if available is not None:
            if str(available).lower() == "true":
                item_obj.available_status = True
            else:
                item_obj.available_status = False

        # ---------- IMAGE UPDATE ----------
        if item_image:
            uploaded_image = upload_image(item_image, "item_image/", "item_")
            item_obj.item_image = uploaded_image

        item_obj.save()

        return Response({
            "status": '1',
            "msg": "Item Updated Successfully",
            "item_id": item_obj.id
        })

    except StoreProduct.DoesNotExist:
        return Response({"status": '0', "msg": "Invalid item"})
    except ItemCategoryMaster.DoesNotExist:
        return Response({"status": '0', "msg": "Invalid category"})
    except:
        print(str(traceback.format_exc()))
        return Response({
            "status": '0',
            "msg": "Something went wrong",
            "error": str(traceback.format_exc())
        })


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def store_delete_item_api(request):
    try:
        data = request.data
        item_id = data['item_id']

        item_obj = StoreProduct.objects.get(id=item_id)
        item_obj.delete()

        return Response({
            "status": '1',
            "msg": "Item Deleted Successfully"
        })

    except StoreProduct.DoesNotExist:
        return Response({"status": '0', "msg": "Invalid item"})
    except:
        print(str(traceback.format_exc()))
        return Response({
            "status": '0',
            "msg": "Something went wrong",
            "error": str(traceback.format_exc())
        })


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def approve_order_api(request):
    try :
        data = request.data
        order_id = data.get("order_id")  
        order_obj = OrdersTable.objects.get(id = order_id)  
        order_obj.order_status = "Approved"
        order_obj.save() 
        message_body = f'{order_obj.fk_business.name} has approved the order.'
        send_notification(message_body, order_obj.fk_users.token, 'Admin', 'Order Approved', order_obj.fk_users.id, 'Order')
        return JsonResponse({"status":200,'msg':"Order Approved Successfully"})
    except:
        traceback.print_exc()
        return JsonResponse({"Status":403,"msg":"Something Went Wrong"})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def complete_order_api(request):
    try :
        data = request.data
        order_id = data.get("order_id")  
        order_obj = OrdersTable.objects.get(id = order_id)  
        order_obj.order_status = "Completed"
        order_obj.save() 
        message_body = f'{order_obj.fk_business.name} has completed the order.'
        send_notification(message_body, order_obj.fk_users.token, 'Admin', 'Order Completed', order_obj.fk_users.id, 'Order')
        return JsonResponse({"status":200,'msg':"Order Completed Successfully"})
    except:
        traceback.print_exc()
        return JsonResponse({"Status":403,"msg":"Something Went Wrong"})


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import traceback

from .models import SupportTicket


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def submit_support_ticket_api(request):
    try:
        data = request.data
        user_id = data.get("user_id")
        category = data.get("category")
        message = data.get("message")

        if not user_id or not message:
            return JsonResponse({"status":400, "msg":"Missing required fields"})

        ticket_obj = SupportTicket.objects.create(
            user_id_id=user_id,
            category=category,
            message=message,
            status="open"
        )

        return JsonResponse({
            "status": 200,
            "msg": "Support ticket submitted successfully",
            "ticket_id": ticket_obj.id
        })

    except:
        traceback.print_exc()
        return JsonResponse({"status":403, "msg":"Something Went Wrong"})


import ast
from django.core.mail import EmailMessage

from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.shortcuts import redirect
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from datetime import datetime
from django.shortcuts import render
import json
import traceback
import random
import base64
from random import randint
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, status
import requests
import os
from rest_framework.views import APIView
import datetime

# Create your views here

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


#########################################################


################ EMail Send Master API ################
def send_mail(subject, message, email):
    try:
        from_email = settings.EMAIL_HOST_USER
        email_msg = EmailMessage(subject, message, to=[email], from_email=from_email)
        email_msg.send()
        return "success"
    except Exception as e:
        print(str(traceback.format_exc()))
        # print(str(e)
        return "error"


################ EMail Send Master API ################


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def Doctor_Signup_api(request):
    try:
        data = request.data
        response = Response()

        mobile_no = data['mobile_no']
        mobile_otp = "1234"

        if User_Details.objects.filter(mobile_no=mobile_no).exists():

            return Response({'status': 403, "msg": 'Mobile No is Already Resgistered.'})

        else:
            obj = User_Details.objects.create(mobile_no=mobile_no)
            return Response({'status': 200, "msg": 'Doctor register successfully.',
                             "Mobile_no": mobile_no, "mobile_otp": mobile_otp,"user_id":str(obj.id)})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def create_profile_and_set_availability(request):
    try:
        data = request.data
        response = Response()
        user_id  = data['user_id']
        name = data['name']
        email = data['email']
        about_me = data['about_me']
        bussiness_name = data['bussiness_name']
        bussiness_address = data['bussiness_address']
        map_location = data['map_location']
        latitude = data['latitude']
        user_type = data['user_type']
        longitude = data['longitude']
        profile_image = data['profile_image']
        shift_list = data['shift_list']

        user_name = data['user_name']
        mobile_no = data['mobile_no']
        country_code = data['country_code']
        password = data['password']
        sign_up_status = data['sign_up_status']
        address = data['address']
        token = data['token']

        path = settings.BASE_DIR + "/media/"

        if User_Details.objects.filter(email=email).exists():

            return Response({'status': 403, "msg": 'Email ID is Already Resgistered.'})



        if profile_image:
            profile_image = upload_image(profile_image, "profile_image/", "profile_")
        else:
            profile_image = ""


        # -------------------------
        # LOCATION (Default Nagpur)
        # -------------------------
        DEFAULT_LATITUDE = '21.118064'
        DEFAULT_LONGITUDE = '79.0450328'

        latitude = data.get('latitude') or DEFAULT_LATITUDE
        longitude = data.get('longitude') or DEFAULT_LONGITUDE

        
        
        obj = User_Details.objects.filter(id = user_id)[0]
        User_Details.objects.filter(id = user_id).update(user_name=user_name, password=password, mobile_no=mobile_no, email=email, name=name,
                           about_me=about_me, bussiness_name=bussiness_name, bussiness_address=bussiness_address,
                           map_location=map_location, latitude=latitude, longitude=longitude,
                           country_code=country_code,
                           profile_image=profile_image, user_type=user_type, status=True, token=token,
                           sign_up_status=sign_up_status, created_datetime=datetime.datetime.now(), address=address , is_profile_create = True)
        # obj.save()

        for i in shift_list:
            doc_obj = Set_Availability(fk_doctor_id=user_id, add_shift=i['Shift_name'], from_shift=i['From_time'],
                                       to_shift=i['To_time'], select_days=i['Selectd_days'])

            doc_obj.save()

        return Response({'status': 200, "msg": 'Account is created', "doctor_id": user_id, "user_type": obj.user_type,
                         "name": obj.name, "email": obj.email, "mobile_no": obj.mobile_no,
                         "map_location": obj.map_location, "latitude": obj.latitude, "longitude": obj.longitude,
                         'pro_image': profile_image})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def login_doctor_api(request):
    try:
        data = request.data
        response = Response()
        email = data['email']
        password = data['password']
        token = data['token']

        if User_Details.objects.filter(email=email, password=password).exists():

            doc_obj = User_Details.objects.get(email=email, password=password)
            doc_obj.token = token
            doc_obj.save()

            return Response(
                {'status': 200, "msg": 'Login Successfull', "doctor_id": doc_obj.id, "doctor_name": doc_obj.name})
        else:
            return Response({'status': 403, "msg": 'Invalid Credential...'})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def Doctor_service_api(request):
    try:
        data = request.data
        response = Response()
        doctor_id = data['fk_doctor'] 
        if User_Details.objects.filter(id=doctor_id).exists(): 
            serializer = DoctorServiceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save() 
                return Response({'status': 200, "msg": 'Service is created.', "service_id": serializer.data['id']})
            else:
                return Response({'status': 403, "msg": 'Mobile Number is not Registered'})
        else:
            return Response({'status': 403, "msg": 'Account is not Exist'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_manage_service_api(request):
    try:
        data = request.data
        response = Response()
        doctor_id = data['fk_doctor'] 
        doc_list = []
        doc_dict = {} 
        if User_service.objects.filter(fk_doctor_id=doctor_id).exists(): 
            doc_obj = User_service.objects.filter(fk_doctor_id=doctor_id)
            for i in doc_obj:
                doc_dict['service_id'] = i.id
                doc_dict['title'] = i.title
                doc_dict['description'] = i.description
                doc_dict['pet_type'] = i.pet_type
                doc_dict['charges'] = i.charges
                doc_dict['created_at'] = i.created_at
                doc_list.append(doc_dict)
                doc_dict = {}

            return Response({'status': 200, "msg": 'Service List', "Service List": doc_list})
        else:
            return Response({'status': 403, "msg": 'Service is not created'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def Edit_service_manage_api(request):
    try:
        data = request.data
        response = Response()
        service_id = data['service_id']
        title = data['title']
        description = data['description']
        pet_type = data['pet_type']
        charges = data['charges']
         
        if User_service.objects.filter(id=service_id).exists():
            update_doc_obj = User_service.objects.filter(id=service_id).update(title=title, description=description,pet_type=pet_type, charges=charges)
            return Response({'status': 200, "msg": 'Service is updated successfully'})
        else: 
            return Response({'status': 403, "msg": 'No Doctors service found.'}) 
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def Delete_service_manage_api(request):
    try:
        data = request.data
        response = Response()
        service_id = data['service_id']

        if User_service.objects.filter(id=service_id).exists():

            update_doc_obj = User_service.objects.filter(id=service_id).delete()

            return Response({'status': 200, "msg": 'Service is deleted successfully'})
        else:
            return Response({'status': 403, "msg": 'No Doctors service found.'})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def upcoming_doctors_appointment_list_api(request):
    try:
        doc_id = request.data.get('doc_id')
        if not doc_id:
            return Response({"status": 400, "msg": "doc_id required"}, status=400)

        today = timezone.now().date()

        obj = DoctorsAppointment.objects.select_related(
            'doctor', 'client', 'fk_pet'
        ).filter(
            doctor_id=doc_id,
            booking_date__gte=today,
            book_status="Booked"
        ).order_by('booking_date', 'booking_time')[:50]

        serializer = DoctorsAppointmentSerializer(obj, many=True)
        print(serializer.data, "------")
        return Response({
            'status': 200,
            'msg': "Doctors appointment details",
            'payload': serializer.data
        })

    except Exception:
        logger.exception("Upcoming doctor appointment API failed")
        return Response(
            {"status": 500, "msg": "Internal server error"},
            status=500
        )


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def edit_doctor_profile_api(request):
    try:
        data = request.data
        id = data['id']
        if User_Details.objects.filter(id=id).exists():
            doc_obj = User_Details.objects.get(id=id)
            serializer = UserDetailSerializer(doc_obj, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 200, "msg": 'Profile is updated successfully'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 403, "msg": 'No Doctors service found.'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def add_shift_api(request):
    try:
        data = request.data
        # if Set_Availability.objects.filter(fk_doctor_id=data['id'], add_shift=data['Shift_name'],
        #                                    from_shift=data['From_time'],
        #                                    to_shift=data['To_time'], select_days=data['Selectd_days']).exists():
        Set_Availability.objects.create(fk_doctor_id=data['doc_id'], add_shift=data['Shift_name'],
                                        from_shift=data['From_time'],
                                        to_shift=data['To_time'], select_days=data['Selectd_days'])
        return Response({'status': 200, "msg": 'Availability added for doctor.'})
        # else:
        #     return Response({'status': 403, "msg": 'Availability already added.'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def edit_shift_api(request):
    try:
        data = request.data
        Set_Availability.objects.filter(id=data['id']).update(fk_doctor_id=data['doc_id'], add_shift=data['Shift_name'],
                                                              from_shift=data['From_time'],
                                                              to_shift=data['To_time'],
                                                              select_days=data['Selectd_days'])
        return Response({'status': 200, "msg": 'Availability updated for doctor.'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def delete_shift_api(request):
    try:
        data = request.data
        Set_Availability.objects.filter(id=data['id']).delete()
        return Response({'status': 200, "msg": 'Availability deleted for doctor.'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})


@api_view(['POST'])
@permission_classes((AllowAny,))
@csrf_exempt
def get_doctors_availability_list_api(request):
    try:
        data = request.data
        obj = Set_Availability.objects.filter(fk_doctor__id=data['doc_id'])
        dct = {}
        lst = []
        for i in obj:
            dct['id'] = str(i.id)
            dct['fk_doctor'] = str(i.fk_doctor.id)
            dct['add_shift'] = str(i.add_shift)
            dct['from_shift'] = str(i.from_shift)
            dct['to_shift'] = str(i.to_shift)
            dct['select_days'] = ast.literal_eval(i.select_days) if i else []
            lst.append(dct)
            dct = {}
        return Response({'status': 200, "msg": 'Doctors availability list.', 'payload': lst})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})
 
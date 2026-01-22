from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.shortcuts import redirect
from .serializers import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from datetime import datetime

import json
import traceback
import random
import base64
from random import randint
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions
import requests
import os
from rest_framework.views import APIView


# Create your views here

###################### Upload image ##################### 
def upload_image(img,img_path,img_name):
    path = settings.BASE_DIR + "/media/"
    # path = "/media/"
    random_number = '{:04}'.format(random.randrange(1, 10**4))
    imgN = img_path+img_name+random_number+"_"+'.jpg'
    destination = open(path+imgN, 'wb')
    # img = img.resize((1000, 1000), Image.ANTIALIAS)   
    destination.write(base64.b64decode(img))
    destination.close() 
   
    return imgN
 #########################################################


    
@api_view(['POST'])
@permission_classes((AllowAny, ))
@csrf_exempt
def sitter_signup_api(request):
    try:
        data = request.data
        response = Response()
        
        mobile_no = data['mobile_no']   
        mobile_otp = "1234"
        
        if User_Details.objects.filter(mobile_no = mobile_no).exists():
        
            return Response({'status':403 , "msg":'Mobile No is Already Resgistered'})
            
        else:
    
            return Response({'status':200 , "msg":'Click on Ok to receive OTP at your registered mobile number', "Mobile_no": mobile_no, "mobile_otp": mobile_otp})
     
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error":str(traceback.format_exc())})



@api_view(['POST'])
@permission_classes((AllowAny, ))
@csrf_exempt
def create_sitter_account(request):
    try:
        data = request.data
        response = Response()

        user_type = data['user_type']
        profile_image = data['profile_image']
        name = data['name']
        email = data['email']
        password = data['password']
        mobile_no = data['mobile_no']
        map_location = data['map_location']
        latitude = data['latitude']
        longitude = data['longitude']
        sign_up_status = data['sign_up_status']
        address = data['address']
        
    
        # -------------------------
        # LOCATION (Default Nagpur)
        # -------------------------
        DEFAULT_LATITUDE = '21.118064'
        DEFAULT_LONGITUDE = '79.0450328'

        latitude = data.get('latitude') or DEFAULT_LATITUDE
        longitude = data.get('longitude') or DEFAULT_LONGITUDE
        
        if profile_image:
            profile_upload_image = upload_image(profile_image, "profile_image/", "profile_")      
        else:
            profile_upload_image = ""
            
        User_obj = User_Details(name = name, email = email, password = password, mobile_no = mobile_no,sign_up_status = sign_up_status,user_type = user_type, profile_image= profile_upload_image, map_location = map_location,latitude = latitude,longitude = longitude, status = True, created_datetime = datetime.now(),address = address)
                                
        User_obj.save()
            
        return Response({'status':200 , "msg":'Account is Created Successfully', "sitter_id":User_obj.id })

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error":str(traceback.format_exc())})    
        
        


@api_view(['POST'])
@permission_classes((AllowAny, ))
@csrf_exempt
def login_sitter_api(request):
    try:
        data = request.data
        response = Response()    
        email = data['email']
        password = data['password']

        if User_Details.objects.filter(email = email, password = password).exists():
            
            sit_obj = User_Details.objects.get(email = email, password = password)
        
            return Response({'status':200, "msg":'Login Successfull', "sitter_id":sit_obj.id})
        else:
            return Response({'status':403, "msg":'Invalid Credential.'})
    
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error":str(traceback.format_exc())})        
        

@api_view(['POST'])
@permission_classes((AllowAny, ))
@csrf_exempt
def create_sitter_service_api(request):
    try:
        data = request.data
        response = Response()
        sitter_id = data['fk_doctor']
               
        if User_Details.objects.filter(id = sitter_id).exists():   
        
            serializer = DoctorServiceSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
              
                return Response({'status':200 , "msg":'Sitter Service is create', "sitter_service_id": serializer.data['id']})
            else:
                return Response({'status':403 , "msg":'Account is not Registered'})
        else:
            return Response({'status':403 , "msg":'Account is not Exist'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error":str(traceback.format_exc())})

        


@api_view(['GET'])
@permission_classes((AllowAny, ))
@csrf_exempt
def get_sitter_service_api(request):
    try:
        data = request.data
        response = Response()
        sitter_id = data['fk_doctor']
        
        doc_list = []
        doc_dict = {}
        
        if User_Details.objects.filter(id = sitter_id).exists():
     
            sit_obj = User_service.objects.filter(fk_doctor_id = sitter_id)
            
            for i in sit_obj:
                doc_dict['sitter_service_id'] = str(i.id) if i.id else ""
                doc_dict['title'] = str(i.title) if i.title else ""
                doc_dict['description'] = str(i.description) if i.description else ""
                doc_dict['pet_type'] = str(i.pet_type) if i.pet_type else ""
                doc_dict['charges'] = str(i.charges) if i.charges else ""
                doc_list.append(doc_dict)
                doc_dict = {}              
        
            return Response({'status':200 , "msg":'Sitters Service List', "Service List" : doc_list})
        else:
            return Response({'status':403 , "msg":'Service is not created'})
    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error":str(traceback.format_exc())})
        
        

    
@api_view(['POST'])
@permission_classes((AllowAny, ))
@csrf_exempt
def delete_sitter_service_api(request):
    try:
        data = request.data
        response = Response()    
        service_id = data['sitter_service_id']
                
        if User_service.objects.filter(id = service_id).exists(): 
            
            update_doc_obj = User_service.objects.filter(id = service_id).delete()
            
            return Response({'status':200 , "msg":'Sitter Service is deleted successfully'})           
        else:   
            return Response({'status':403 , "msg":'No Sitter service found.'})

    except:
        print(str(traceback.format_exc()))
        return Response({"status": 403, "msg": "Something went wrong", "error":str(traceback.format_exc())})
                
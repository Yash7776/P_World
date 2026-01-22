from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from datetime import datetime,date
from .models import *
from django.template.loader import render_to_string
import traceback 
import calendar
from dateutil import relativedelta
from django.views.decorators.cache import cache_control
import yaml
import h3
import ast


#Cart_Count
def Cart_Count(request):
    cust_id = request.session.get('customer_id')
    if not cust_id:
        return 0

    user_obj = User_Details.objects.filter(id=cust_id).first()
    if not user_obj:
        return 0

    return AddtoCart.objects.filter(fk_user=user_obj).count()


#dashboard 
def dashboard(request):
    return render(request, 'admin_panel/dashboard.html')

#terms_and_conditions 
def terms_and_conditions(request):
    return render(request, 'customer/terms_and_conditions.html')

#login_page
def login_page(request):
    return render(request, 'admin_panel/login_page.html')

#customer_list
def customer_list(request):
    if request.session.get('user_id'):
        cus_obj = User_Details.objects.filter(user_type="Customer").order_by('name')
        return render(request, 'admin_panel/customer_list.html', {'cus_obj': cus_obj})
    else:
        return redirect("/")

#user_list
def user_list(request, user_type):
    if not request.session.get('user_id'):
        return redirect("/")
    # Normalize user_type (Doctor, Salon, Walker, etc.)
    user_type = user_type.capitalize()
    obj = User_Details.objects.filter(user_type=user_type)
    # Dynamic page title
    title_map = {
        "Doctor": "List of Doctors",
        "Sitter": "List of Sitters",
        "Trainer": "List of Trainers",
        "Salon": "List of Salons",
        "Walker": "List of Walkers",
        "Store": "List of Stores",
        "Customer": "List of Customers",
    }
    page_title = title_map.get(user_type, "User List")
    return render(
        request,
        "admin_panel/doctor_list.html",
        {
            "obj": obj,
            "user_type": user_type,
            "page_title": page_title,
        }
    )

#vendor_appointment_list
def vendor_appointment_list(request, vendor_type):
    if request.session.get('user_id'): 
        start_date = datetime.today().replace(day=1)
        date = datetime.date(start_date)
        end_date = date.replace(day = calendar.monthrange(date.year, date.month)[1]) 
        lists = []
        obj = DoctorsAppointment.objects.filter(vendor_type=vendor_type,booking_date__gte = start_date, booking_date__lte = end_date).order_by('-booking_date')
        for i in obj :   
            data = {
            "vendor_name" : i.doctor.name,
            "customer_name" : i.client.name,
            "pet_name" : i.fk_pet.pet_name,
            "service" : i.services_title,
            "booking_date": i.booking_date,
            "booking_time": i.booking_time,
            "book_status": i.book_status,
            "amount": i.amount,
            "date": i.date,
            "time": i.time,
            }
            lists.append(data)
        return render(request, 'admin_panel/vendor_appointment_list.html', {'obj': lists, 'vendor_type': vendor_type})
    else:
        return redirect("/")

#render_to_doctor_detail
def render_to_doctor_detail(request, id):
    if request.session.get('user_id'):
        try:
            doc_obj = User_Details.objects.get(id=id)
            apt_obj = User_service.objects.filter(
                fk_doctor__id=id
            ).order_by('-id')
            availability_qs = Set_Availability.objects.filter(
                fk_doctor__id=id
            ).order_by('id')
            availability_obj = []
            for avail in availability_qs:
                days_list = []
                if avail.select_days:
                    try:
                        # converts '["Sunday","Monday"]' → ['Sunday', 'Monday']
                        days_list = ast.literal_eval(avail.select_days)
                    except Exception:
                        days_list = []
                availability_obj.append({
                    "obj": avail,
                    "days": days_list
                })
            return render(
                request,
                'admin_panel/render_to_doctor_detail.html',
                {
                    'doc_obj': doc_obj,
                    'apt_obj': apt_obj,
                    'availability_obj': availability_obj,
                    'user_type': doc_obj.user_type
                }
            )
        except User_Details.DoesNotExist:
            messages.error(request, 'User not found')
            return redirect('/admin_panel/users/')
    else:
        return redirect('/')

#login_check
@csrf_exempt
def login_check(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if not Admin_login.objects.filter(username=username, password=password).exists():
        return HttpResponse("error")
    else:
        obj = Admin_login.objects.get(username=username, password=password)
        request.session['user_id'] = str(obj.id)
        return HttpResponse("success")

#logout
@csrf_exempt
def logout(request):
    try:
        del request.session['user_id']
        print("logout")
        return redirect("/")
    except:
        return redirect("/")

#delete_doctor_entry
@csrf_exempt
def delete_doctor_entry(request):
    doc_id = request.POST.get('doc_id')
    doc_obj = User_Details.objects.filter(id=doc_id).delete()
    return HttpResponse("deleted")

#delete_customer_entry
@csrf_exempt
def delete_customer_entry(request):
    cus_id = request.POST.get('cus_id')
    cus_obj = User_Details.objects.filter(id=cus_id).delete()
    return HttpResponse("deleted")

#get_customer_detail
@csrf_exempt
def get_customer_detail(request):
    cust_id = request.POST.get('id')
    obj = User_Details.objects.get(id=cust_id)
    cust_obj = {
        'mobile_no': obj.mobile_no,
        'country_code': obj.country_code,
        'email': obj.email,
        'name': obj.name,
        'address': obj.address,
        'profile_image': obj.profile_image.url if obj.profile_image else '',
    }
    return JsonResponse(cust_obj)

#doctor_booking_detail
@csrf_exempt
def doctor_booking_detail(request):
    return render(request, 'admin_panel/doctor-booking-detail.html')

#filter_appointment_page
@csrf_exempt
def filter_appointment_page(request):
    status = request.POST.get('status')
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    vendor_type = request.POST.get('vendor_type')
    lists = []
    if request.session.get('user_id'):
        if status == 'All':
            obj = DoctorsAppointment.objects.filter(vendor_type=vendor_type,booking_date__gte=from_date, booking_date__lte=to_date).order_by( '-booking_date')
        else:
            obj = DoctorsAppointment.objects.filter(vendor_type=vendor_type, book_status=status, booking_date__gte=from_date, booking_date__lte=to_date).order_by('-booking_date')
        for i in obj :  
            data = {
            "vendor_name" : i.doctor.name,
            "customer_name" : i.client.name,
            "pet_name" : i.fk_pet.pet_name,
            "service" : i.services_title,
            "booking_date": i.booking_date,
            "booking_time": i.booking_time,
            "book_status": i.book_status,
            "amount": i.amount,
            "date": i.date,
            "time": i.time,
            }
            lists.append(data)
        render = render_to_string('admin_panel/filter-appointment.html', {'obj': lists,"vendor_type":vendor_type})
        return HttpResponse(render)
    else:
        return redirect("/")
   


 ############################################### webisite panel #################################

#webiste home page
# def index(request): 
#     total_doctors = User_Details.objects.filter(user_type = 'Doctor').count()
#     customer_obj = User_Details.objects.filter(user_type = 'Customer')
#     saloon_obj = User_Details.objects.filter(user_type = 'Salon')
#     store_obj = User_Details.objects.filter(user_type = 'Store')
#     sitter_obj = User_Details.objects.filter(user_type = 'Sitter')
#     trainer_obj = User_Details.objects.filter(user_type = 'Trainer')
#     walker_obj = User_Details.objects.filter(user_type = 'Walker')
#     # doctors_obj = UserRatingReview.objects.raw("select m.id, m.fk_user_receiver_id, avg(m.rating) as RatingAvg from P_World_App_userratingreview as m group by m.fk_user_receiver_id ORDER BY RatingAvg DESC")    ### raw query for group by rating and order by rating in decending order   
#     doctors_obj = UserRatingReview.objects.raw(
#             "SELECT MIN(m.id) AS id, m.fk_user_receiver_id, AVG(m.rating) AS RatingAvg "
#             "FROM P_World_App_userratingreview AS m "
#             "GROUP BY m.fk_user_receiver_id "
#             "ORDER BY RatingAvg DESC"
#         )
#     for i in doctors_obj:
#         print(i.fk_user_receiver.user_type)
#     have_pets = None
#     if request.session.get("customer_email") and request.session.get("customer_id") :
#         cust_id = request.session.get("customer_id")
#         if New_Pet.objects.filter(fk_customer__id = cust_id).exists():
#             have_pets = 'Yes'
#         else :
#             have_pets = 'No' 
#     context = {
#     'doctors_obj':doctors_obj,
#     'total_doctors':total_doctors,
#     'total_customers': customer_obj.count(),
#     'total_saloon': saloon_obj.count(),
#     'total_store': store_obj.count(),
#     'total_sitter': sitter_obj.count(),
#     'total_trainer': trainer_obj.count(),
#     'total_walker': walker_obj.count(),
#     'have_pets': have_pets,
#     'Item_count':Cart_Count(request)
#     }
#     return render(request, 'customer/index.html',context)
from django.db.models import Count, Avg
from django.core.cache import cache

def index(request):
    # Counts
    user_counts = User_Details.objects.values('user_type').annotate(count=Count('id'))
    counts_dict = {item['user_type']: item['count'] for item in user_counts}

    # Top doctors (cached)
    top_doctors = cache.get('top_doctors')
    if not top_doctors:
        top_doctors = list(
            User_Details.objects.filter(user_type='Doctor')
            .annotate(RatingAvg=Avg('rating_receiver__rating'))
            .values('id', 'name', 'RatingAvg')
            .order_by('-RatingAvg')[:10]
        )
        cache.set('top_doctors', top_doctors, 600)  # cache 10 min

    # Pet check
    cust_id = request.session.get("customer_id")
    have_pets = 'Yes' if cust_id and New_Pet.objects.filter(fk_customer_id=cust_id).exists() else 'No'

    context = {
        'doctors_obj': top_doctors,
        'total_doctors': counts_dict.get('Doctor', 0),
        'total_customers': counts_dict.get('Customer', 0),
        'total_salon': counts_dict.get('Salon', 0),
        'total_store': counts_dict.get('Store', 0),
        'total_sitter': counts_dict.get('Sitter', 0),
        'total_trainer': counts_dict.get('Trainer', 0),
        'total_walker': counts_dict.get('Walker', 0),
        'have_pets': have_pets,
        'Item_count': Cart_Count(request),
    }

    return render(request, 'customer/index.html', context)



# service details page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def service_details(request,v_id): 
    my_date = date.today()
    todays_day = calendar.day_name[my_date.weekday()]  
    user_obj = User_Details.objects.get(id = v_id) 
    ratings_obj = UserRatingReview.objects.filter(fk_user_receiver = user_obj).order_by('-id')
    available_obj = Set_Availability.objects.filter(fk_doctor= user_obj) 
    service_obj = User_service.objects.filter(fk_doctor= user_obj) 
    pet_obj = None
    new_age = None
    first_value = None
    if request.session.get("customer_email") :
        pet_obj = New_Pet.objects.filter(fk_customer__email=request.session.get("customer_email")).order_by('-id')
    rating = 0
    avg_rating = 0
    avalability_list = []
    if ratings_obj:
        for i in ratings_obj:
            rating = i.rating + rating
        avg_rating = rating/ratings_obj.count()
    if available_obj:
        for i in available_obj: 
            if todays_day  in i.select_days:
                data = {
                'from_shift' : i.from_shift,
                'to_shift' : i.to_shift,
                }
                avalability_list.append(data)
    if pet_obj :
        for i in pet_obj:
            birth_date = datetime.strptime(str(i.birth_date), "%Y-%m-%d")
            today_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d")
            calculate_age = relativedelta.relativedelta(today_date,birth_date)
            
            if calculate_age.years == 0 and calculate_age.months == 0 :
                i.age = f"{calculate_age.days} days"
            elif calculate_age.years == 0 :
                i.age = f"{calculate_age.months} months" 
            else :
                i.age = f"{calculate_age.years} year {calculate_age.months} months"
        first_value = pet_obj.first()
        new_age = first_value.age    
    context = {
    'user_obj': user_obj,
    "rating": avg_rating,
    'ratings_obj':ratings_obj,
    'total_review': ratings_obj.count(),
    'available_obj':avalability_list,
    'service_obj':service_obj,
    'pet_obj':pet_obj,
    'Item_count':Cart_Count(request),
    'first_value':first_value,
    'new_age':new_age
    }
    return render(request, 'customer/services.html', context)


#customer login page
def customer_login(request):
    if request.session.get("customer_email") and request.session.get("customer_id") :
        return redirect("/index/")
    else :
        return render(request, 'customer/login.html')
    
#forgot password page
def forgot_password(request):
    return render(request, 'customer/forgot_password.html')
 
#function for logout website 
def customer_logout(request):
    try:
        del request.session['customer_email'] 
        del request.session['customer_id'] 
        del request.session['user_type'] 
        return redirect("/index/")
    except:
        return redirect("/index/")
        
#customer sign up page        
def customer_signup(request):
    country_obj = CountryMaster.objects.all()
    if request.session.get('customer_email') :
        del request.session['customer_email'] 
    if  request.session.get('customer_id') :   
        del request.session['customer_id'] 
    if request.session.get('user_type')  :    
        del request.session['user_type'] 
    context = {
    'country_obj':country_obj,
    }
    return render(request, 'customer/signup.html',context)
 
#add new pet page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_pets(request):
    if request.session.get("customer_email") and request.session.get("customer_id") :
        pet_obj = PetMaster.objects.all()
        context = {
        'pet_obj':pet_obj,
        'Item_count':Cart_Count(request)
        }
        return render(request, 'customer/add_pet.html',context)
    else :
        return redirect("/index/")
        
#add_new_pet     
@csrf_exempt
def add_new_pet(request):
    try:
        if request.method == "POST":
            customer_id = request.POST.get('fk_customer')
            pet_name = request.POST.get('pet_name')
            type_of_pet = request.POST.get('type_of_pet')
            breed = request.POST.get('breed')
            birth_date = request.POST.get('birth_date')
            gender = request.POST.get('gender')
            weight = request.POST.get('weight')
            pet_description = request.POST.get('pet_description')
            pet_image = request.FILES.get('pet_image')
            obj = New_Pet(pet_name=pet_name, type_of_pet=type_of_pet, breed=breed, birth_date=birth_date, gender=gender,
                          weight=weight, pet_description=pet_description, created_datetime=datetime.now(),
                          fk_customer_id=customer_id, pet_image=pet_image)
            obj.save() 
            return JsonResponse({'status': 200, "msg": 'New Pet Added Successfully'})
        return JsonResponse({"status": 403, "msg": "Something went wrong"})
    except: 
        return JsonResponse({"status": 403, "msg": "Something went wrong"})
        
#show_pets      
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_pets(request):
    if request.session.get("customer_email") and request.session.get("customer_id") :
        user_obj = User_Details.objects.filter(email = request.session.get("customer_email"))
        pets = New_Pet.objects.filter(fk_customer = user_obj[0])
        context = {
        "pets":pets,
        'Item_count':Cart_Count(request)
        }
        return render(request, 'customer/show_pets.html',context)
    else :
        return redirect("/index/")


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)       
# def show_venders(request,obj):
#     data_list = []
#     todays_day = calendar.day_name[date.today().weekday()]  
#     doctors_obj = User_Details.objects.filter(user_type = obj)  
#     # rating_obj = UserRatingReview.objects.raw("select m.id, m.fk_user_receiver_id, avg(m.rating) as RatingAvg from P_World_App_userratingreview as m group by m.fk_user_receiver_id")   
#     from django.db.models import Avg
#     rating_obj = UserRatingReview.objects.values('fk_user_receiver_id').annotate(RatingAvg=Avg('rating'))
#     rating = None
#     is_available = None
#     user_obj = None 
#     if request.session.get('customer_id') :
#         user_obj = User_Details.objects.get(id = request.session.get('customer_id') )
#     for i in doctors_obj: 
#         available_obj = Set_Availability.objects.filter(fk_doctor= i)  
#         if available_obj:
#             is_available = 0
#             for k in available_obj: 
#                 if k.select_days and todays_day in k.select_days:
#                     is_available = 1
#             if is_available == 1 : 
#                 rating = 0
#                 for j in rating_obj: 
#                     if j['fk_user_receiver_id'] == i.id:
#                         rating = j['RatingAvg']
#                 distance = 0
#                 if user_obj and user_obj.latitude and i.latitude :
#                     coords_1 = (float(user_obj.latitude) , float(user_obj.longitude))
#                     coords_2 = (float(i.latitude) , float(i.longitude))
#                     distance = round(h3.point_dist(coords_1, coords_2, unit='km'),1)
#                 data = {
#                     'id' : i.id,  
#                     'user_name' : i.user_name ,  
#                     'mobile_no' : i.mobile_no,  
#                     'country_code' : i.country_code,  
#                     'email' : i.email ,
#                     'name' : i.name,
#                     'about_me' : i.about_me , 
#                     'bussiness_name' : i.bussiness_name, 
#                     'bussiness_address' : i.bussiness_address, 
#                     'map_location' : i.map_location , 
#                     'latitude' : i.latitude  ,
#                     'longitude' : i.longitude , 
#                     'address' : i.address ,
#                     'profile_image' : i.profile_image,
#                     'rating': rating,
#                     'distance': distance,
#                 }
#                 data_list.append(data)
#     string = render_to_string('render_to_string/r_t_s_all_doctors.html',{'data_list' : sorted(data_list, key=lambda x: x['rating'], reverse=True)})
#     context = {
#     'data_list': data_list, 
#     'string': string,
#     'vender_type': obj,
#     'Item_count':Cart_Count(request)
#     }
#     return render(request,'customer/all_doctors.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_venders(request, obj):
    data_list = []
    todays_day = calendar.day_name[date.today().weekday()]
    print("TODAY'S DAY:", todays_day)

    doctors_obj = User_Details.objects.filter(user_type=obj)
    print(f"Found {doctors_obj.count()} users of type '{obj}'")

    rating_obj = UserRatingReview.objects.values('fk_user_receiver_id').annotate(RatingAvg=Avg('rating'))
    print("Ratings fetched:", list(rating_obj))

    user_obj = None
    if request.session.get('customer_id'):
        try:
            user_obj = User_Details.objects.get(id=request.session.get('customer_id'))
            print("Logged in customer:", user_obj.user_name)
        except User_Details.DoesNotExist:
            print("Customer ID in session not found in DB")
    
    for doctor in doctors_obj:
        print("\n=== Doctor:", doctor.user_name, doctor.id, "===")

        # Check availability objects
        available_obj = Set_Availability.objects.filter(fk_doctor=doctor)
        print(f"Availability entries found: {available_obj.count()}")
        
        availability_days = []
        for avail in available_obj:
            print("Availability record:", avail.add_shift, avail.from_shift, avail.to_shift, avail.select_days)
            if avail.select_days:
                # Process select_days safely
                try:
                    # Convert JSON-like strings to Python list
                    import ast
                    days = ast.literal_eval(avail.select_days)
                except:
                    days = [day.strip() for day in avail.select_days.split(',')]
                availability_days.extend(days)
        
        print("Availability days processed:", availability_days)

        # Calculate rating
        rating = 0
        for r in rating_obj:
            if r['fk_user_receiver_id'] == doctor.id:
                rating = r['RatingAvg']
        print("Rating:", rating)

        # Calculate distance
        distance = 0
        if user_obj and user_obj.latitude and doctor.latitude and doctor.longitude:
            try:
                coords_1 = (float(user_obj.latitude), float(user_obj.longitude))
                coords_2 = (float(doctor.latitude), float(doctor.longitude))
                distance = round(h3.point_dist(coords_1, coords_2, unit='km'), 1)
            except Exception as e:
                print("Distance calculation error:", e)
                distance = 0
        print("Distance from user:", distance)

        # Prepare data
        data = {
            'id': doctor.id,
            'user_name': doctor.user_name,
            'mobile_no': doctor.mobile_no,
            'country_code': doctor.country_code,
            'email': doctor.email,
            'name': doctor.name,
            'about_me': doctor.about_me,
            'bussiness_name': doctor.bussiness_name,
            'bussiness_address': doctor.bussiness_address,
            'map_location': doctor.map_location,
            'latitude': doctor.latitude,
            'longitude': doctor.longitude,
            'address': doctor.address,
            'profile_image': doctor.profile_image,
            'rating': rating,
            'distance': distance,
            'availability_days': availability_days,
        }
        data_list.append(data)

    print("\nTotal doctors to display:", len(data_list))
    string = render_to_string('render_to_string/r_t_s_all_doctors.html',
                              {'data_list': sorted(data_list, key=lambda x: x['rating'] if x['rating'] else 0, reverse=True)})

    context = {
        'data_list': data_list,
        'string': string,
        'vender_type': obj,
        'Item_count': Cart_Count(request),
    }

    return render(request, 'customer/all_doctors.html', context)

## filter vendor by distance or rating
@csrf_exempt
def filter_vendor_by(request):
    try : 
        if request.method == "POST":
            filter_by = request.POST.get('filter_by')
            vendor_type = request.POST.get('vendor_type')
            data_list = []
            todays_day = calendar.day_name[date.today().weekday()]  
            doctors_obj = User_Details.objects.filter(user_type = vendor_type)  
            rating_obj = UserRatingReview.objects.raw("select m.id, m.fk_user_receiver_id, avg(m.rating) as RatingAvg from P_World_App_userratingreview as m group by m.fk_user_receiver_id")   
            rating = None
            is_available = None 
            user_obj = None 
            if request.session.get('customer_id') :
                user_obj = User_Details.objects.get(id = request.session.get('customer_id') )
            for i in doctors_obj: 
                available_obj = Set_Availability.objects.filter(fk_doctor= i)  
                if available_obj:
                    is_available = 0
                    for k in available_obj: 
                        if todays_day  in k.select_days:
                            is_available = 1
                    if is_available == 1 : 
                        rating = 0
                        for j in rating_obj: 
                            if j.fk_user_receiver == i:
                                rating = j.RatingAvg 
                        distance = 0
                        if user_obj and user_obj.latitude and i.latitude :
                            coords_1 = (float(user_obj.latitude) , float(user_obj.longitude))
                            coords_2 = (float(i.latitude) , float(i.longitude))
                            distance = round(h3.point_dist(coords_1, coords_2, unit='km'),1)
                        data = {
                            'id' : i.id,  
                            'user_name' : i.user_name ,  
                            'mobile_no' : i.mobile_no,  
                            'country_code' : i.country_code,  
                            'email' : i.email ,
                            'name' : i.name,
                            'about_me' : i.about_me , 
                            'bussiness_name' : i.bussiness_name, 
                            'bussiness_address' : i.bussiness_address, 
                            'map_location' : i.map_location , 
                            'latitude' : i.latitude  ,
                            'longitude' : i.longitude , 
                            'address' : i.address ,
                            'profile_image' : i.profile_image,
                            'rating': rating,
                            'distance': distance,
                        }
                        data_list.append(data)
            if  filter_by == 'rating':
                data_list = sorted(data_list, key=lambda x: x['rating'], reverse=True)    
            else : 
                data_list = sorted(data_list, key=lambda x: x['distance'] )            
            string = render_to_string('render_to_string/r_t_s_all_doctors.html',{'data_list' : data_list})
                
            return JsonResponse({'status':1, "string" :string})
        else :
            return JsonResponse({'status':0, "msg": "Something Went Wrong."})
    except:
        return JsonResponse({'status':0, "msg": "Something Went Wrong."})
        
#function for filter trainer sitter walker by distance or rating 
@csrf_exempt
def filter_TSW_vendors_by(request):
    if request.method == "POST":
        filter_by = request.POST.get('filter_by') 
        vendor_type = ['Trainer','Sitter','Walker']
        vendor_data = []  
        todays_day = calendar.day_name[date.today().weekday()]  
        rating_obj = UserRatingReview.objects.raw("select m.id, m.fk_user_receiver_id, avg(m.rating) as RatingAvg from P_World_App_userratingreview as m group by m.fk_user_receiver_id")   
        rating = None
        is_available = None
        user_obj = None 
        if request.session.get('customer_id') :
            user_obj = User_Details.objects.get(id = request.session.get('customer_id') )
        for v in vendor_type :
            data_list = []
            vendor_obj = User_Details.objects.filter(user_type = v) 
            for i in vendor_obj: 
                available_obj = Set_Availability.objects.filter(fk_doctor= i)  
                if available_obj:
                    is_available = 0
                    for k in available_obj: 
                        if todays_day  in k.select_days:
                            is_available = 1
                    if is_available == 1 : 
                        rating = 0
                        for j in rating_obj: 
                            if j.fk_user_receiver == i:
                                rating = j.RatingAvg  
                        distance = 0
                        if user_obj and user_obj.latitude and i.latitude :
                            coords_1 = (float(user_obj.latitude) , float(user_obj.longitude))
                            coords_2 = (float(i.latitude) , float(i.longitude))
                            distance = round(h3.point_dist(coords_1, coords_2, unit='km'),1)        
                        data = {
                            'id' : i.id,  
                            'user_name' : i.user_name ,  
                            'mobile_no' : i.mobile_no,  
                            'country_code' : i.country_code,  
                            'email' : i.email ,
                            'name' : i.name,
                            'about_me' : i.about_me , 
                            'bussiness_name' : i.bussiness_name, 
                            'bussiness_address' : i.bussiness_address, 
                            'map_location' : i.map_location , 
                            'latitude' : i.latitude  ,
                            'longitude' : i.longitude , 
                            'address' : i.address ,
                            'profile_image' : i.profile_image,
                            'rating': rating,
                            "distance":distance,
                        }
                        data_list.append(data) 
            if filter_by == "rating" :
                data_list = sorted(data_list, key=lambda x: x['rating'], reverse=True) 
            else :
                data_list = sorted(data_list, key=lambda x: x['distance'] ) 
            temp_data = {
            "vendor_type" : v,
            "data_list" : data_list,
            }            
            vendor_data.append(temp_data)            
        string = render_to_string('render_to_string/r_t_s_show_all_vendors.html',{"vendor_data":vendor_data})  
        return JsonResponse({"status":1, "string":string})
    else :
        return JsonResponse({"status":0})
        
#cart page
def cart(request):
    return render(request, 'customer/cart.html')
 
#checkout page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkout(request):
    if request.session.get("customer_email") and request.session.get("customer_id") :  
        user_email = request.session.get("customer_email")
        user_obj = User_Details.objects.get(email = user_email)
        new_var = User_Details.objects.get(email = user_email).id
        address = None 
        if deliveryAddress.objects.filter(fk_users_id = new_var).exists() : 
            address = deliveryAddress.objects.get(fk_users_id = new_var) 
        address_obj = None
        if deliveryAddress.objects.filter(fk_users = user_obj).exists() : 
            address_obj = deliveryAddress.objects.get(fk_users = user_obj)
            if address_obj.province :
                address_obj.province_id = ProvinceMaster.objects.get(name = address_obj.province).id
            if address_obj.city :
                address_obj.city_id = CityMaster.objects.filter(city = address_obj.city)[0].id
            if address_obj.country :
                address_obj.country_id = CountryMaster.objects.get(name = address_obj.country).id 
                address_obj.country_code = address_obj.country_code[1:] 
        else : 
            address_obj = User_Details.objects.get(email = user_email)
            address_obj.province_id = 0
            address_obj.city_id = 0
            address_obj.country_id = CountryMaster.objects.get(name = address_obj.country).id 
        country_obj = CountryMaster.objects.all()
        province_obj = ProvinceMaster.objects.filter(country_id = CountryMaster.objects.get(name = address_obj.country).id)
        cart_item = AddtoCart.objects.filter(fk_user__email = user_email)
        sub_total = 0
        total_quantity = cart_item.count()
        total_amount = 0
        delivery_charges = 100
        convinience_fee = 40
        for i in cart_item:
            sub_total = i.total_item_price + sub_total
        total_amount = delivery_charges + convinience_fee + sub_total
        string = render_to_string('render_to_string/r_t_s_cart_items.html',{"cart_item":cart_item})
        context = {
        'country_obj':country_obj,
        'address_obj' : address_obj,
        'province_obj' : province_obj, 
        'string': string,
        'sub_total':sub_total,
        'total_amount':total_amount,
        'delivery_charges':delivery_charges,
        'convinience_fee':convinience_fee,
        'total_quantity':total_quantity,
        'Item_count':Cart_Count(request),
        'address':address
        }
        return render(request, 'customer/checkout.html' , context) 
    else :
        return redirect("/index/")
        
#get_state_of_country  
@csrf_exempt        
def get_state_of_country(request):
    if request.method == 'POST':
        province_id = request.POST.get('province_id')
        city_obj = CityMaster.objects.filter(state_id = province_id).values()
        return JsonResponse({'status': '1','data': list(city_obj)})
    return JsonResponse({'status':'0'})

#Get_Province
@csrf_exempt
def Get_Province(request):
    try:
        if request.method == 'POST':
            country_id = request.POST.get('country_id')
            country_obj = CountryMaster.objects.filter(id = country_id)[0]
            province_obj = ProvinceMaster.objects.filter(country_id = country_id).values()  
            return JsonResponse({'status': '1','data': list(province_obj),'country':country_obj.country_code})
        else:
            return JsonResponse({'status':'0'})
    except:
        return JsonResponse({'status':'0'})
  
#doctors_appointment
def doctors_appointment(request):
    if request.session.get("user_type") and  request.session.get("user_type") == "Doctor" and request.session.get('customer_email') :
        import datetime
        today = datetime.date.today()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        doctor_obj = User_Details.objects.get(email = request.session.get('customer_email'))
        appointment = DoctorsAppointment.objects.filter(doctor = doctor_obj, book_status='Booked', booking_date__gte = today , booking_date__lte = tomorrow ).order_by("-booking_date") 
        past_appointment = DoctorsAppointment.objects.filter(doctor = doctor_obj, booking_date__lte = yesterday ).order_by("-booking_date") 
        if User_service.objects.filter(fk_doctor__email = request.session.get('customer_email')).exists() :
            services = True
        else : 
            services = False
        if Set_Availability.objects.filter(fk_doctor__email = request.session.get('customer_email')).exists() :
            availability = True
        else :
            availability = False
        context = {
        "appointment" : appointment,
        "availability" : availability,
        "services" : services,
        "past_appointment" : past_appointment,
        }     
        return render(request, "vendors/doctors_appointment.html",context)
    else :
        return redirect("/login/")

#show_all_doctors_appointment        
def show_all_doctors_appointment(request):
    if request.session.get("user_type") and  request.session.get("user_type") == "Doctor" and request.session.get('customer_email') : 
        doctor_obj = User_Details.objects.get(email = request.session.get('customer_email'))
        appointment = DoctorsAppointment.objects.filter(doctor = doctor_obj).order_by("-booking_date") 
        context = {
        "appointment" : appointment,
        }     
        return render(request, "vendors/show_all_doctors_appointment.html",context)
    else :
        return redirect("/login/")
        
#add_services  
def add_services(request):
    if request.session.get("user_type") and  request.session.get("user_type") != "Customer" and request.session.get('customer_email') : 
        pet_obj = PetMaster.objects.all()
        context = {
        "pet_obj": pet_obj,
        }
        return render(request, "vendors/add_doctor_services.html" , context )
    else :
        return redirect("/login/")
        
#manage_services     
def manage_services(request):
    if request.session.get("user_type") and  request.session.get("user_type") != "Customer" and request.session.get('customer_email') : 
        services = User_service.objects.filter(fk_doctor__email = request.session.get('customer_email')) 
        pet_obj = PetMaster.objects.all()
        context={
        "services" : services,
         "pet_obj": pet_obj,
        }
        return render(request, "vendors/show_doctor_services.html",context  )
    else :
        return redirect("/login/")
        
#doctor_availability        
def doctor_availability(request):
    if request.session.get("user_type") and  request.session.get("user_type") != "Customer" and request.session.get('customer_email') : 
        count = Set_Availability.objects.filter(fk_doctor__email = request.session.get('customer_email')).count()
        pet_obj = PetMaster.objects.all() 
        count = count + 1
        context={ 
         "count": count, 
        }
        return render(request, "vendors/doctor_availability.html",context  )
    else :
        return redirect("/login/")
        
#show_doctor_availability   
def show_doctor_availability(request):
    if request.session.get("user_type") and  request.session.get("user_type") != "Customer" and request.session.get('customer_email') : 
        doctor_obj= User_Details.objects.get(email = request.session.get('customer_email'))
        avalability = Set_Availability.objects.filter(fk_doctor = doctor_obj) 
        for i in avalability: 
            data = []
            for j in yaml.safe_load(i.select_days): 
                data.append(j)   
            i.days = data 
        context={
        "avalability" : avalability, 
        }
        return render(request, "vendors/show_doctor_availability.html",context  )
    else :
        return redirect("/login/")
        
#set_doctor_availability
@csrf_exempt
def set_doctor_availability(request): 
    try:
        if request.method == "POST" :
            from_shift = request.POST.get('from_shift')
            to_shift = request.POST.get('to_shift')
            doctor_email = request.POST.get('doctor_email')
            days = request.POST.get('days')
            shift = request.POST.get('shift')
            doctor_obj= User_Details.objects.get(email = doctor_email)
            Set_Availability.objects.create(fk_doctor = doctor_obj, add_shift=shift, from_shift= from_shift,  to_shift= to_shift , select_days = days ) 
            if User_service.objects.filter(fk_doctor__email =  doctor_email).exists() :
                services = True
            else :
                services = False
            return JsonResponse({'status': 200, "msg": 'Availability Added Successfully.', 'services' : services})
        return JsonResponse({"status": 403, "msg": "Something went wrong"})    
    except:
        print(str(traceback.format_exc()))
        return JsonResponse({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})

#delete_doctor_shift 
@csrf_exempt
def delete_doctor_shift(request): 
    try:
        if request.method == "POST" :
            shift_id = request.POST.get('shift_id')
            from_shift = request.POST.get('from_shift')
            Set_Availability.objects.filter(id = shift_id).delete() 
            return JsonResponse({'status': 200, "msg": 'Doctor Shift deleted Successfully.'}) 
        return JsonResponse({"status": 403, "msg": "Something went wrong"})    
    except:
        print(str(traceback.format_exc()))
        return JsonResponse({"status": 403, "msg": "Something went wrong", "error": str(traceback.format_exc())})
  
#bookings   
def bookings(request):
    if request.session.get("user_type") == "Salon"  or  request.session.get("user_type") == "Walker" or  request.session.get("user_type") == "Sitter" or  request.session.get("user_type") == "Trainer" : 
        import datetime
        today = datetime.date.today()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1) 
        yesterday = datetime.date.today() - datetime.timedelta(days=1) 
        doctor_obj = User_Details.objects.get(email = request.session.get('customer_email'))
        bookings = DoctorsAppointment.objects.filter(doctor = doctor_obj, book_status='Booked', booking_date__gte = today , booking_date__lte = tomorrow ).order_by("-booking_date") 
        past_bookings = DoctorsAppointment.objects.filter(doctor = doctor_obj, booking_date__lte = yesterday ).order_by("-booking_date") 
        if User_service.objects.filter(fk_doctor__email = request.session.get('customer_email')).exists() :
            services = True
        else : 
            services = False
        if Set_Availability.objects.filter(fk_doctor__email = request.session.get('customer_email')).exists() :
            availability = True
        else :
            availability = False
        context = {
        "bookings" : bookings,
        "availability" : availability,
        "services" : services,
        "past_bookings" : past_bookings,
        }     
        return render(request, "vendors/bookings.html", context )
    else :
        return redirect("/login/")
    
#show_all_bookings         
def show_all_bookings(request):
    if request.session.get("user_type") == "Salon"  or  request.session.get("user_type") == "Walker" or  request.session.get("user_type") == "Sitter" or  request.session.get("user_type") == "Trainer" : 
        doctor_obj = User_Details.objects.get(email = request.session.get('customer_email'))
        bookings = DoctorsAppointment.objects.filter(doctor = doctor_obj, book_status='Booked' ).order_by("-booking_date") 
        context = {
        "bookings" : bookings,
        }     
        return render(request, "vendors/show_all_bookings.html", context )
    else :
        return redirect("/login/")

#add_iitem
def add_item(request):
    if request.session.get("user_type") == "Store" :
        print("iiiiii")
        pet_obj = PetMaster.objects.all().order_by("-id")
        item_category = ItemCategoryMaster.objects.all().order_by("-id")
        context = {
        'pet_obj':pet_obj,
        'item_category':item_category, 
        }
        return render(request, "vendors/add_item.html", context)
    else :
        return redirect("/login/")

#add_new_item        
@csrf_exempt
def add_new_item(request): 
    if request.method == "POST":
        item_image = request.FILES.get("item_image")
        title = request.POST.get("title")
        item_category_id = request.POST.get("item_type")
        pet_type = request.POST.get("pet_type")
        description = request.POST.get("description")
        charges = request.POST.get("charges")
        available = request.POST.get("available")
        fk_vendor_id = request.POST.get("fk_vendor")
        category_obj = ItemCategoryMaster.objects.get(id = item_category_id )
        vendor_obj = User_Details.objects.get(id= fk_vendor_id) 
        if available == 'true':
            available = True
        else :
            available = False
        ItemMaster.objects.create(fk_vendor=vendor_obj ,fk_category = category_obj, item_name = title,item_price=charges,item_image = item_image,pet_type = pet_type,item_description = description, available_status = available ) 
        return JsonResponse({"status":1, "msg" : 'Item Added Successfully.'})
    else :         
        return JsonResponse({"status":0,"msg" : 'Something Went Wrong...'})    
   
#show_vendors_item     
def show_vendors_item(request):
    if request.session.get("user_type") == "Store" : 
        item_obj = ItemMaster.objects.filter(fk_vendor__id = request.session.get("customer_id") ).order_by('-id') 
        context = { 
        'item_obj' : item_obj,
        }
        return render(request, "vendors/show_items.html", context)
    else :
        return redirect("/login/")

#store_dashboard        
def store_dashboard(request):
    if request.session.get("user_type") == "Store" :
        vendor_obj = User_Details.objects.filter(email = request.session.get("customer_email"))
        vendor = User_Details.objects.get(email = request.session.get("customer_email"))
        start_date = datetime.today().replace(day=1)
        date = datetime.date(start_date) 
        end_date = date.replace(day = calendar.monthrange(date.year, date.month)[1]) 
        order_obj = OrderItemTable.objects.filter(fk_orders__fk_business = vendor,fk_orders__order_status = 'Pending',booking_date__gte = start_date,booking_date__lte = end_date )
        print(order_obj)
        list_data = []
        order_obj_list = []        
        for i in order_obj :
            print(i)
            if i.fk_orders not in order_obj_list :
                obj = {
                "order_no": i.fk_orders.order_no,
                "booking_date": i.fk_orders.booking_date,
                "total_amount": i.fk_orders.total_amount,
                "order_status": i.fk_orders.order_status,
                "id": i.fk_orders.id,
                }
                list_data.append(obj)
                print(list_data)
        data = {
        "order_obj" : list_data,
        
        } 
        string = render_to_string('render_to_string/r_t_s_vendor_orders.html',data)
        context = {
        "string" : string,
        "from_date" : start_date,
        "to_date" : end_date, 
        }
        return render(request, "vendors/store_dashboard.html",context)
    else :
        return redirect("/login/")

#delete_store_item       
@csrf_exempt           
def delete_store_item(request):
    if request.method == "POST" :
        item_id = request.POST.get("id")
        ItemMaster.objects.get(id=item_id).delete()   
        return JsonResponse({"status":1,"msg" : 'Item Deleted Successfully..'})    
    else :
        return JsonResponse({"status":0,"msg" : 'Something Went Wrong...'})    
    
#edit_item      
def edit_item(request, id):
    if request.session.get("user_type") == "Store" :
        pet_obj = PetMaster.objects.all().order_by("-id")
        item_category = ItemCategoryMaster.objects.all().order_by("-id")
        item_obj = ItemMaster.objects.get(id = id ) 
        context = {
        'pet_obj':pet_obj,
        'item_category':item_category, 
        'item_obj' : item_obj,
        }
        return render(request, "vendors/edit_store_item.html",context)
    else :
        return redirect("/login/")
       
#edit_store_item      
@csrf_exempt
def edit_store_item(request): 
    if request.method == "POST":
        item_image = request.FILES.get("item_image")
        item_id = request.POST.get("item_id")
        title = request.POST.get("title")
        item_category_id = request.POST.get("item_type")
        pet_type = request.POST.get("pet_type")
        description = request.POST.get("description")
        charges = request.POST.get("charges")
        available = request.POST.get("available")
        fk_vendor_id = request.POST.get("fk_vendor")
        category_obj = ItemCategoryMaster.objects.get(id = item_category_id )
        vendor_obj = User_Details.objects.get(id= fk_vendor_id) 
        if available == 'true':
            available = True
        else :
            available = False 
        item_obj = ItemMaster.objects.get(id=item_id)
        item_obj.fk_category = category_obj
        item_obj.item_name = title
        item_obj.item_price=charges
        item_obj.pet_type = pet_type
        item_obj.item_description = description
        item_obj.item_price=charges
        item_obj.available_status = available 
        if item_image != None : 
            item_obj.item_image =  item_image
        item_obj.save()
        return JsonResponse({"status":1, "msg" : 'Item Edited Successfully.'})
    else :         
        return JsonResponse({"status":0,"msg" : 'Something Went Wrong...'})    

#filter_vendor_order   
@csrf_exempt
def filter_vendor_order(request):
    if request.method == "POST":
        status = request.POST.get("status") 
        vendor = User_Details.objects.get(email = request.session.get("customer_email"))
        from_date = datetime.today().replace(day=1)
        date = datetime.date(from_date)
        to_date = date.replace(day = calendar.monthrange(date.year, date.month)[1]) 
        order_obj = OrderItemTable.objects.filter(fk_orders__fk_business = vendor , fk_orders__order_status = status,booking_date__gte = from_date,booking_date__lte = to_date )  
        list_data = []
        order_obj_list = []        
        for i in order_obj :
            if i.fk_orders not in order_obj_list :
                obj = {
                "order_no": i.fk_orders.order_no,
                "booking_date": i.fk_orders.booking_date,
                "total_amount": i.fk_orders.total_amount,
                "order_status": i.fk_orders.order_status,
                "id": i.fk_orders.id,
                }
                list_data.append(obj)
        data = {
        "order_obj" : list_data,
        } 
        string = render_to_string('render_to_string/r_t_s_vendor_orders.html',data) 
        return JsonResponse({"status":1,'from_date':from_date,"to_date":to_date,"string":string})
    else :         
        return JsonResponse({"status":0,"msg" : 'Something Went Wrong...'})          

#filter_vendor_order_by_date        
@csrf_exempt
def filter_vendor_order_by_date(request):
    if request.method == "POST":
        status = request.POST.get("status")
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")  
        print(status)
        order_obj = OrderItemTable.objects.filter(fk_vendors__email = request.session.get("customer_email") , fk_orders__order_status = status,booking_date__gte = from_date,booking_date__lte = to_date )  
        list_data = []
        order_obj_list = []        
        for i in order_obj :
            if i.fk_orders not in order_obj_list :
                obj = {
                "order_no": i.fk_orders.order_no,
                "booking_date": i.fk_orders.booking_date,
                "total_amount": i.fk_orders.total_amount,
                "order_status": i.fk_orders.order_status,
                "id": i.fk_orders.id,
                }
                list_data.append(obj)
        data = {
        "order_obj" : list_data,
        } 
        string = render_to_string('render_to_string/r_t_s_vendor_orders.html',data) 
        return JsonResponse({"status":1,'from_date':from_date,"to_date":to_date,"string":string})
    else :         
        return JsonResponse({"status":0,"msg" : 'Something Went Wrong...'})          

#change_order_status       
@csrf_exempt
def change_order_status(request):
    if request.method == "POST":
        change_status = request.POST.get("change_status")
        status = request.POST.get("status")
        order_id = request.POST.get("order_id") 
        from_date = request.POST.get("from_date") 
        to_date = request.POST.get("to_date") 
        print(order_id)
        obj = OrdersTable.objects.get(id = order_id)
        obj.order_status = change_status
        if change_status == "Cancelled" :
            obj.cancelled_by = 'Vendor'
            msg = "Order Cancelled Successfully..."
        else : 
            msg = "Order Approved Successfully..."
        obj.save()
        order_obj = OrderItemTable.objects.filter(fk_vendors__email = request.session.get("customer_email") , fk_orders__order_status = status,booking_date__gte = from_date,booking_date__lte = to_date )  
        list_data = []
        order_obj_list = []        
        for i in order_obj :
            if i.fk_orders not in order_obj_list :
                obj = {
                "order_no": i.fk_orders.order_no,
                "booking_date": i.fk_orders.booking_date,
                "total_amount": i.fk_orders.total_amount,
                "order_status": i.fk_orders.order_status,
                "id": i.fk_orders.id,
                }
                list_data.append(obj)
        data = {
        "order_obj" : list_data,
        } 
        string = render_to_string('render_to_string/r_t_s_vendor_orders.html',data) 
        return JsonResponse({"status":1,"string":string,"msg":msg })
    else :         
        return JsonResponse({"status":0,"msg" : 'Something Went Wrong...'})       

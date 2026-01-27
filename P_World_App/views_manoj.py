from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from datetime import datetime
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from dateutil import relativedelta
from django.views.decorators.cache import cache_control
import traceback
from datetime import datetime , date
import random
import calendar
import h3
from haversine import haversine
from django.db.models import Count, Q
from django.db.models import Sum

def Cart_Count(request):
    if request.session.get('customer_id'):
        user_obj = User_Details.objects.filter(id = request.session.get('customer_id'))[0]
        Item_count = AddtoCart.objects.filter(fk_user = user_obj).count()
        return Item_count
    else:
        return redirect("/index/")
        
from django.utils import timezone
from datetime import datetime, time as datetime_time

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Reminder(request):
    if request.session.get('customer_email'):
        user = request.session.get('customer_email')
        user_obj = User_Details.objects.get(email=user)
        
        # Get filter parameters
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        
        # Get all reminders for the user
        reminder_queryset = Add_Pet_Reminder.objects.filter(fk_user=user_obj, reminder_status=True)
        
        # Apply date filters if provided
        if from_date:
            reminder_queryset = reminder_queryset.filter(select_date__gte=from_date)
        if to_date:
            reminder_queryset = reminder_queryset.filter(select_date__lte=to_date)
        
        # Get current date and time
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        # Separate upcoming and expired reminders
        upcoming_reminders = []
        expired_reminders = []
        
        for reminder in reminder_queryset:
            reminder_date = reminder.select_date
            reminder_time = reminder.select_time if reminder.select_time else datetime_time(23, 59, 59)
            
            # Compare dates
            if reminder_date > today:
                # Future date - upcoming
                upcoming_reminders.append(reminder)
            elif reminder_date == today:
                # Today - check time
                if reminder_time >= current_time:
                    upcoming_reminders.append(reminder)
                else:
                    expired_reminders.append(reminder)
            else:
                # Past date - expired
                expired_reminders.append(reminder)
        
        # Sort reminders by date and time
        upcoming_reminders.sort(key=lambda x: (x.select_date, x.select_time or datetime_time(0, 0)))
        expired_reminders.sort(key=lambda x: (x.select_date, x.select_time or datetime_time(0, 0)), reverse=True)
        
        context = {
            'upcoming_reminders': upcoming_reminders,
            'expired_reminders': expired_reminders,
            'upcoming_count': len(upcoming_reminders),
            'expired_count': len(expired_reminders),
            'Item_count': Cart_Count(request),
            'from_date': from_date,
            'to_date': to_date,
        }
        
        return render(request, 'customer/Reminder.html', context)
    else:
        return redirect("/")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Add_Reminder(request):
    if request.session.get('customer_email'):
        user = request.session.get('customer_email')
        user_obj = User_Details.objects.get(email = user)
        
        pets = New_Pet.objects.filter(fk_customer = user_obj)
        
        for i in pets:
            
            b_date = i.birth_date
            
            birth_date = datetime.strptime(str(b_date), "%Y-%m-%d")
            today_date = datetime.strptime(str(datetime.now().date()), "%Y-%m-%d")
            calculate_age = relativedelta.relativedelta(today_date,birth_date)
            
            if calculate_age.years == 0 and calculate_age.months == 0:
                i.age = f'{calculate_age.months}month {calculate_age.days} day'
            elif calculate_age.years == 0 and calculate_age.months != 0:
                i.age = f'{calculate_age.months} months {calculate_age.days}day'
            elif calculate_age.years != 0 and calculate_age.months != 0:
                i.age = f'{calculate_age.years}year {calculate_age.months}month'
            else:
                pass
            # i.age = calculate_age.months
        return render(request,'customer/add_reminder.html',{'pets':pets,'customer_id':user_obj.id,'Item_count':Cart_Count(request)})
    else:
        return redirect("/")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Edit_Reminder(request,id):
    if request.session.get('customer_email'):
        reminder = Add_Pet_Reminder.objects.get(id = id)
        return render(request,'customer/Edit_Reminder.html',{"reminder":reminder,'Item_count':Cart_Count(request)})
    else:
        return redirect("/")
        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Edit_Pet(request,id):
    if request.session.get('customer_email'):
        
        pets = New_Pet.objects.filter(id = id)[0]
        category_pet = PetMaster.objects.all()
        
        return render(request,'customer/Edit_Pets.html',{'pets':pets,'category_pet':category_pet,'Item_count':Cart_Count(request)})
    else:
        return redirect("/")


@csrf_exempt
def Save_Edit_Pet(request):
    try:
        if request.session.get('customer_email'):
            if request.method == 'POST':
                pet_id = request.POST.get('pet_id')
                pet_image = request.FILES.get('pet_image')
                pet_name = request.POST.get('pet_name')
                type_of_pet = request.POST.get('type_of_pet')
                breed = request.POST.get('breed')
                birth_date = request.POST.get('birth_date')
                weight = request.POST.get('weight')
                gender = request.POST.get('gender')
                pet_description = request.POST.get('pet_description')
                
                print(pet_image)
                if pet_image: 
                    pet_obj = New_Pet.objects.get(id = pet_id)
                    New_Pet.objects.filter(id = pet_id).update(pet_name = pet_name , type_of_pet = type_of_pet , breed = breed , birth_date = birth_date , gender = gender, weight = weight , pet_description = pet_description)
                    pet_obj.pet_image = pet_image
                    pet_obj.save()
                else:
                    print("****************")
                    New_Pet.objects.filter(id = pet_id).update(pet_name = pet_name , type_of_pet = type_of_pet , breed = breed , birth_date = birth_date , gender = gender, weight = weight , pet_description = pet_description)   
                     
                return JsonResponse({'status':'1','msg':'Pets Modify Successfully.'})
            else:
                return JsonResponse({'status':'0','msg':'Post method required.'})
        else:
            return redirect("/")
    except:
        return JsonResponse({'status':'0','msg':'Something went wrong.'})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Show_all_services(request):
    vendor_type = ['Trainer', 'Sitter', 'Walker']
    vendor_data = []

    todays_day = calendar.day_name[date.today().weekday()]

    rating_obj = UserRatingReview.objects.raw(
        """
        SELECT id, fk_user_receiver_id, AVG(rating) AS RatingAvg
        FROM P_World_App_userratingreview
        GROUP BY fk_user_receiver_id
        """
    )

    user_obj = None
    customer_id = request.session.get('customer_id')
    if customer_id:
        user_obj = User_Details.objects.filter(id=customer_id).first()

    for v in vendor_type:
        data_list = []
        vendor_obj = User_Details.objects.filter(user_type=v)

        for i in vendor_obj:

            available_obj = Set_Availability.objects.filter(fk_doctor=i)
            is_available = 0

            for k in available_obj:
                if todays_day in k.select_days:
                    is_available = 1
                    break

            if is_available != 1:
                continue

            # ⭐ Rating
            rating = 0
            for j in rating_obj:
                if j.fk_user_receiver_id == i.id:
                    rating = j.RatingAvg or 0
                    break

            # 📍 Distance
            distance = 0
            if (
                user_obj and
                user_obj.latitude and user_obj.longitude and
                i.latitude and i.longitude
            ):
                coords_1 = (float(user_obj.latitude), float(user_obj.longitude))
                coords_2 = (float(i.latitude), float(i.longitude))
                distance = round(haversine(coords_1, coords_2), 1)  # KM

            data = {
                'id': i.id,
                'user_name': i.user_name,
                'mobile_no': i.mobile_no,
                'country_code': i.country_code,
                'email': i.email,
                'name': i.name,
                'about_me': i.about_me,
                'bussiness_name': i.bussiness_name,
                'bussiness_address': i.bussiness_address,
                'map_location': i.map_location,
                'latitude': i.latitude,
                'longitude': i.longitude,
                'address': i.address,
                'profile_image': i.profile_image,
                'rating': rating,
                'distance': distance,
            }

            data_list.append(data)

        # 🔽 Sort vendors by rating
        data_list = sorted(data_list, key=lambda x: x['rating'], reverse=True)

        vendor_data.append({
            "vendor_type": v,
            "data_list": data_list,
        })

    string = render_to_string(
        'render_to_string/r_t_s_show_all_vendors.html',
        {"vendor_data": vendor_data}
    )

    return render(
        request,
        'customer/show_all_services.html',
        {
            'string': string,
            'Item_count': Cart_Count(request)
        }
    )

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Show_Appointments(request):
    if request.session.get('customer_email'):
        user_obj = User_Details.objects.get(email = request.session.get('customer_email'))
        appointment = DoctorsAppointment.objects.filter(client = user_obj,doctor__user_type = "Doctor").order_by('-id')
        for i in appointment: 
            
            try:
                if UserRatingReview.objects.filter(fk_apt = i , fk_user_sender = user_obj).exists():
                    rating_obj = UserRatingReview.objects.filter(fk_apt = i , fk_user_sender = user_obj)[0]
                    i.rating = rating_obj.rating
                    i.review = rating_obj.comment
                    print("-----------")
                else:
                    i.rating  = 0
                    i.review = None
                print(i.rating)
            except:
                traceback.print_exc()
                
        return render(request,'customer/show_appointments.html',{'appointment':appointment,'Item_count':Cart_Count(request)})
    else:
        return redirect("/")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Show_MyBookings(request):
    if request.session.get('customer_email'):
        user_obj = User_Details.objects.get(email = request.session.get('customer_email'))
        print(user_obj.id)
        temp = ['Sitter','Trainer','Walker','salon']
        bookings = DoctorsAppointment.objects.filter(client = user_obj,doctor__user_type__in = temp ).order_by('-id')
        for i in bookings:
            
            try:
                rating_obj = UserRatingReview.objects.get(fk_apt = i , fk_user_sender = user_obj)
                i.rating = rating_obj.rating
                i.review = rating_obj.comment
            except:
                traceback.print_exc()
                i.rating  = 0
                i.review = None
        return render(request,'customer/show_mybookings.html',{'bookings':bookings,'Item_count':Cart_Count(request)})
    else:
        return redirect("/")


from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Edit_Profile_Page(request):
    try:
        session = getattr(request, "session", None)

        # HARD GUARD: session itself can be None
        if not session:
            return redirect("/")

        customer_email = session.get("customer_email")
        customer_id = session.get("customer_id")

        if not customer_email or not customer_id:
            return redirect("/")

        user_obj = User_Details.objects.get(id=customer_id)
        country_obj = CountryMaster.objects.all().order_by("name")

        # Safely handle country_code
        if user_obj.country_code:
            user_obj.country_code = user_obj.country_code.lstrip("+")

        return render(
            request,
            "customer/Edit_Profile.html",
            {
                "user_obj": user_obj,
                "country_obj": country_obj,
                "vendor_type": user_obj.user_type,
                "Item_count": Cart_Count(request),
            },
        )

    except User_Details.DoesNotExist:
        return redirect("/")

    except Exception:
        return redirect("/")


@csrf_exempt
def Edit_Profile(request):
    try:
        if request.session.get('customer_email'):
            if request.method == 'POST':
                profile_image = request.FILES.get('profile_image')
                name = request.POST.get('name')
                email = request.POST.get('email')
                local_address = request.POST.get('local_address')
                address = request.POST.get('address')
                country_code = request.POST.get('country_code')
                mobile = request.POST.get('mobile')
                latitude = request.POST.get('latitude')
                business_name = request.POST.get('business_name')
                business_address = request.POST.get('business_address')
                about = request.POST.get('about')
                longitude = request.POST.get('longitude') 
                if profile_image:
                    user_obj = User_Details.objects.get(id = request.session.get('customer_id'))
                    user_obj.profile_image = profile_image
                    user_obj.save()
                country_obj = CountryMaster.objects.get(id = country_code)
                country_code =  "+" + country_obj.country_code                  
                User_Details.objects.filter(id = request.session.get('customer_id')).update( name = name , email = email , address = local_address , map_location =address ,latitude = latitude,longitude = longitude , country_code = country_code , mobile_no = mobile,bussiness_name = business_name, bussiness_address= business_address,about_me=about, country = country_obj.name )
                return JsonResponse({'status':'1','msg':'Profile Updated Successfully.'})
            else:
                return JsonResponse({'status':'0','msg':'Post method required.'})
        else:
            return redirect("/")
    except:
        traceback.print_exc()
        return JsonResponse({'status':'0','msg':'Something went wrong.'})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Change_Password(request):
    if request.session.get('customer_email'):
        
        return render(request,'customer/change_password.html',{'Item_count':Cart_Count(request)})
    else:
        return redirect("/")

@csrf_exempt
def User_Change_Password(request):
    try:
        if request.session.get('customer_email'):
            if request.method == 'POST':
                old_password = request.POST.get('old_password')
                new_password = request.POST.get('new_password')
                
                user_obj = User_Details.objects.get(id = request.session.get('customer_id'))
                
                if user_obj.password == new_password:
                    return JsonResponse({'status':'0','msg':'Password already exists.'})
                
                if User_Details.objects.filter(id = request.session.get('customer_id') , password = old_password).exists():
                    User_Details.objects.filter(id = request.session.get('customer_id')).update( password = new_password)
                    return JsonResponse({'status':'1','msg':'Password Changed Successfully.'})
                else:
                    return JsonResponse({'status':'0','msg':'Old Password is Incorrect.'})
                
            else:
                return JsonResponse({'status':'0','msg':'Post method required.'})
        else:
            return redirect("/")
    except:
        return JsonResponse({'status':'0','msg':'Something went wrong.'})



@csrf_exempt
def Search_by_Category_Item(request):
    try:
        if request.method == 'POST':
            category_id = request.POST.get('category_id')
            items=None
            if category_id=="All":
                items = StoreItem.objects.filter(available_status = True)
            else:
                items = StoreItem.objects.filter(fk_category__id = category_id,available_status = True).order_by('-id')
            for i in items:
                rating_lst = list(map(lambda a: a.rating, UserRatingReview.objects.filter(fk_user_receiver__id=i.fk_vendor.id)))
                count = UserRatingReview.objects.filter(fk_user_receiver__id=i.fk_vendor.id).count()
                
                if count != 0:
                    i.rating = sum(rating_lst) / count
                else:
                    i.rating = 0.0  
                print(i.rating)
            rendered = render_to_string('render_to_string/r_t_s_product_category.html',{'item':(sorted(items, key=lambda x: x.rating ,reverse = True))})
            return JsonResponse({'status':'1','response':rendered})
        else:
            return JsonResponse({'status':'0','msg':'Post method required.'})
    except:
        return JsonResponse({'status':'0','msg':'Something went wrong.'})

@csrf_exempt
def Search_by_PetType_Item(request):
    try:
        
        if request.method == 'POST':
            pet_type = request.POST.get('pet_type')
            if pet_type=='All':
                items = StoreItem.objects.filter(available_status = True)
            else:
                items = StoreItem.objects.filter(pet_type = pet_type,available_status = True).order_by('-id')
            for i in items:
                rating_lst = list(map(lambda a: a.rating, UserRatingReview.objects.filter(fk_user_receiver__id=i.fk_vendor.id)))
                count = UserRatingReview.objects.filter(fk_user_receiver__id=i.fk_vendor.id).count()
                
                if count != 0:
                    i.rating = sum(rating_lst) / count
                else:
                    i.rating = 0.0  
                print(i.rating)
            rendered = render_to_string('render_to_string/r_t_s_product_category.html',{'item':(sorted(items, key=lambda x: x.rating ,reverse = True))})
            return JsonResponse({'status':'1','response':rendered})
        else:
            return JsonResponse({'status':'0','msg':'Post method required.'})
        
    except:
        traceback.print_exc()
        return JsonResponse({'status':'0','msg':'Something went wrong.'})

#### product items page
@cache_control(no_cache=True, must_revalidate=True, no_store=True) 

def items(request):
    # Base queryset - only available items
    queryset = AllItemMaster.objects.all()

    # ── Pet type filter preparation ───────────────────────────────────────
    # Get distinct pet types + count of available items per pet type
    pet_types = (
        queryset
        .exclude(pet_type__isnull=True)
        .exclude(pet_type='')
        .values('pet_type')
        .annotate(item_count=Count('id'))
        .order_by('pet_type')
    )

    total_count = queryset.count()


    # ── Items to display (initially all) ──────────────────────────────────
    items = queryset.select_related('fk_category').order_by('-created_at')  # or any ordering you prefer

    item_count = Cart_Count(request)

    context = {
        'item': items,               # you'll loop over this in template
        'Item_count': item_count,
        'pets': pet_types,           # list of dicts: {'pet_type': '...', 'item_count': N}
        'total_count': total_count,
    }

    return render(request,'customer/product_category.html', context)
 
#### product details page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_details(request, id):
    item = get_object_or_404(
        AllItemMaster.objects.select_related('fk_category'),
        id=id,
    )

    # Get all StoreItem entries for this master item
    store_items = StoreItem.objects.filter(
        fk_master=item,
        fk_store__status=True,              # only active stores
        fk_store__user_type="Store"         # only real stores
    ).select_related('fk_store')

    store_list = []
    for si in store_items:
        store = si.fk_store
        store_list.append({
            'store': store,
            'price': si.item_price,
            'description': si.item_description.strip() if si.item_description else item.item_name,
          })

    # Optional: sort stores by price (lowest first)
    store_list.sort(key=lambda x: x['price'] or float('inf'))

    # Cart-related logic for this logged-in user
    item_count = None                       # for quantity input pre-fill
    has_this_product_in_cart = False        # for showing "View Cart" button

    customer_id = request.session.get('customer_id')
    if customer_id:
        try:
            user_obj = User_Details.objects.get(id=customer_id)

            # Total quantity of THIS AllItemMaster (any store variant) in user's cart
            total_qty = AddtoCart.objects.filter(
                fk_user=user_obj,
                fk_item__fk_master=item         # ← joins through StoreItem → AllItemMaster
            ).aggregate(total=Sum('quantity'))['total'] or 0

            if total_qty > 0:
                item_count = total_qty
                has_this_product_in_cart = True

        except User_Details.DoesNotExist:
            # Invalid session customer_id → ignore silently
            pass


    context = {
        'item_obj': item,
        'store_list': store_list,
        'distance': None,
        'item_count': item_count,
        'has_this_product_in_cart': has_this_product_in_cart,
        'Item_count': Cart_Count(request),
    }

    return render(request, 'customer/product_details.html', context)

@csrf_exempt
def Item_AddtoCart(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'status': '0', 'msg': 'Post method required.'})

        master_item_id = request.POST.get('item_id')
        store_id       = request.POST.get('store_id')
        quantity       = request.POST.get('quantity')
        customer_id    = request.POST.get('customer_id')

        if not all([master_item_id, store_id, quantity, customer_id]):
            return JsonResponse({'status': '0', 'msg': 'Missing required fields'})

        quantity = int(quantity)

        # Fetch objects
        master_item = get_object_or_404(AllItemMaster, id=master_item_id)
        store       = get_object_or_404(User_Details, id=store_id, user_type="Store", status=True)
        store_item  = get_object_or_404(StoreItem, fk_master=master_item, fk_store=store)
        user_obj    = get_object_or_404(User_Details, id=customer_id)

        delivery_charges = 100
        convenience_fee  = 40   # note: you wrote "convinience" earlier — fix typo if you want

        # Enforce one vendor/store per cart
        if AddtoCart.objects.filter(fk_user=user_obj).exists():
            last_cart = AddtoCart.objects.filter(fk_user=user_obj).last()
            if last_cart.fk_vendor != store:
                return JsonResponse({
                    'status': '0',
                    'msg': 'You can only order products from one store at a time'
                })

        # Check if this exact StoreItem is already in cart
        existing = AddtoCart.objects.filter(fk_user=user_obj, fk_item=store_item).first()

        if existing:
            # Update existing
            updated_total_item_price = store_item.item_price * quantity
            existing.quantity = quantity
            existing.total_item_price = updated_total_item_price
            existing.save()
        else:
            # Create new
            total_item_price = quantity * store_item.item_price
            total_amount = total_item_price + delivery_charges + convenience_fee

            AddtoCart.objects.create(
                fk_item          = store_item,
                fk_vendor        = store,               # ← using existing field
                fk_user          = user_obj,
                quantity         = quantity,
                item_price       = store_item.item_price,
                total_item_price = total_item_price,
                delivery_charge  = delivery_charges,
                taxes            = convenience_fee,
                total_amount     = total_amount
            )

        return JsonResponse({'status': '1', 'msg': 'Item Added Successfully.'})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': '0', 'msg': str(e) or 'Something went wrong.'})
     
@csrf_exempt
def Update_Cart(request):
    try:
        if request.session.get('customer_email'):
            if request.method == 'POST':
                item_id = request.POST.get('item_id')
                update_quantity = request.POST.get('update_quantity')
                item_price = request.POST.get('item_price')
                
                
                user_obj = User_Details.objects.filter(id = request.session.get('customer_id'))[0]
                
                total_item_price = int(update_quantity) * float(item_price)
                AddtoCart.objects.filter(id = item_id).update(quantity = update_quantity , total_item_price = total_item_price)
                cart_item = AddtoCart.objects.filter(fk_user = user_obj)
                sub_total = 0
                total_quantity = 0
                total_amount = 0
                delivery_charges = 100
                convinience_fee = 40
                
                for i in cart_item:
                    sub_total = i.total_item_price + sub_total
                    total_quantity = i.quantity + total_quantity
                    
                total_amount = delivery_charges + convinience_fee + sub_total
                return JsonResponse({'status':'1','sub_total':sub_total,'total_amount':total_amount})
            else:
                return JsonResponse({'status':'0','msg':'Post method required.'})
        return redirect("/")
    except:
        traceback.print_exc()
        return JsonResponse({'status':'0','msg':'Something went wrong.'})
  
  
@csrf_exempt
def Remove_Cart_Item(request):
    try:
        if request.session.get("customer_email") and request.session.get("customer_id"):
            if request.method == 'POST':
                item_id = request.POST.get('item_id')
                user_obj = User_Details.objects.filter(id = request.session.get('customer_id'))[0]
                AddtoCart.objects.filter(id =item_id).delete()
                cart_item = AddtoCart.objects.filter(fk_user = user_obj)
                
                sub_total = 0
                total_quantity = 0
                total_amount = 0
                delivery_charges = 100
                convinience_fee = 40
                
                for i in cart_item:
                    sub_total = i.total_item_price + sub_total
                    total_quantity = i.quantity + total_quantity
                    
                total_amount = delivery_charges + convinience_fee + sub_total
                string = render_to_string('render_to_string/r_t_s_cart_items.html',{"cart_item":cart_item})
                return JsonResponse({'status':'1','msg':'Item Remove Successfully.','response':string,'sub_total':sub_total,'total_amount':total_amount,'Item_count':Cart_Count(request)})
            else:
                return JsonResponse({'status':'0','msg':'Post method required.'})
        else:
            return redirect("/")
    except:
        traceback.print_exc()
        return JsonResponse({'status':'0','msg':'Something went wrong.'})


@csrf_exempt
def Place_Order(request):
    try:
        
        if request.method == 'POST':
            sub_total = request.POST.get('sub_total')
            total_amount = request.POST.get('total_amount')
            delivery_charge = request.POST.get('delivery_charge')
            convinience_fee = request.POST.get('convinience_fee')
            total_quantity = request.POST.get('total_quantity')
            customer_id = request.POST.get('customer_id')  
            # Get Address details 
            name = request.POST.get('name')
            email = request.POST.get('email')
            address1 = request.POST.get('address1')
            address2 = request.POST.get('address2')
            country_code = request.POST.get('country_code')
            mobile = request.POST.get('mobile')
            province = request.POST.get('province')
            city = request.POST.get('city')
            postal_code = request.POST.get('postal_code')
            country_id = request.POST.get('country_id')
            note = request.POST.get('note') 
            fk_business = request.POST.get('fk_business_id')
            country_obj = CountryMaster.objects.filter(id = country_id)[0]
            province_obj = ProvinceMaster.objects.filter(id = province)[0]
            city_obj = CityMaster.objects.filter(id = city)[0]
            
            user_obj = User_Details.objects.filter(id = customer_id)[0] 
            # save delivery address
            if deliveryAddress.objects.filter(fk_users = user_obj).exists():
               deliveryAddress.objects.filter(fk_users = user_obj).update(name = name , email = email , address1 = address1 , address2 = address2, country_code = country_code , mobile_no = mobile , province = province_obj.name , city = city_obj.city , postalcode = postal_code,country  = country_obj.name)
            else:
                deliveryAddress.objects.create(fk_users = user_obj , name = name , email = email , address1 = address1 , address2 = address2, country_code = country_code , mobile_no = mobile , province = province_obj.name , city = city_obj.city , postalcode = postal_code,country  = country_obj.name)
             
            # save order details 
            booking_time = datetime.now().time()
            booking_date = datetime.now().date()
            cart_obj = AddtoCart.objects.filter(fk_user = user_obj)
            
            cart = AddtoCart.objects.filter(fk_user = user_obj)
            ###Generate Order no
            order_no = "OID"+ str(random.randint(100000,999999))
            while OrdersTable.objects.filter(order_no=order_no).exists():
                order_no = "OID"+ str(random.randint(100000,999999))   
                
            order_obj = OrdersTable.objects.create( order_no = order_no ,fk_users = user_obj ,booking_time = booking_time, booking_date = booking_date ,order_status = "Pending",delivery_note = note,status = True, name = name , email = email , address1 = address1 , address2 = address2, country_code = country_code , mobile_no = mobile , province = province_obj.name , city = city_obj.city , postalcode = postal_code,country  = country_obj.name,  fk_business_id=fk_business )
            subtotal = 0 
            quantity = 0 
            total_amount = 0 
            for i in cart : 
                # item_obj = StoreItem.objects.filter(id = i.fk_item.id)[0]
                # vend_id = StoreItem.objects.get(id = i.fk_item.id).id   
                item_obj = StoreItem.objects.get(id=i.fk_item.id)
                vend_id = item_obj.fk_vendor.id  # Get the vendor's user ID
                item_total_price = i.quantity * i.item_price
                OrderItemTable.objects.create(fk_orders = order_obj , fk_item = item_obj , fk_vendors_id = vend_id , item_quantity = i.quantity , item_price = i.item_price,item_total_price = item_total_price)
                
                subtotal = i.total_item_price + subtotal
                quantity = i.quantity + quantity
                delivery_charge = i.delivery_charge  
                taxes = i.taxes 
                
            total_amount = subtotal + delivery_charge + taxes
                
            order_obj.item_price =  subtotal
            order_obj.total_quantity =   quantity 
            order_obj.delivery_charge =  delivery_charge
            order_obj.taxes = taxes
            order_obj.total_amount =  total_amount
            order_obj.save()
            AddtoCart.objects.filter(fk_user = user_obj).delete()
            
            return JsonResponse({'status':'1','msg':'Order Placed Successfully.'})
        else:
            return JsonResponse({'status':'0','msg':'Post method required.'})
        
    except:
        traceback.print_exc()
        return JsonResponse({'status':'0','msg':'Something went wrong.'})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def OrderHistory(request):
    if request.session.get('customer_email'):
        user_obj = User_Details.objects.filter(id = request.session.get('customer_id'))[0]
        orders = OrdersTable.objects.filter(fk_users = user_obj).order_by('-id')
        # orders = OrderItemTable.objects.filter(fk_orders__in = user_orders)
        return render(request,'customer/order_history.html',{'order':orders,'Item_count':Cart_Count(request)})
    else:
        return redirect("/index/")

@csrf_exempt
def Order_Item_Detail(request):
    try:
        if request.session.get('customer_email'):
            if request.method == "POST":
                order_id = request.POST.get('order_id')
                order_obj = OrdersTable.objects.filter(id = order_id)[0]
                order_item = OrderItemTable.objects.filter(fk_orders = order_obj)
                rendered = render_to_string('render_to_string/r_t_s_item_detail.html',{'order_item':order_item})
                return JsonResponse({'status':'1','response':rendered })
            else:
                return JsonResponse({'status':'0','msg':'Post method required.'})
        else:
            return redirect("/index/")
    except:
        return JsonResponse({'status':'0','msg':'Something went wrong.'})
def Temp(request):
    return render(request,'customer/temp.html')

def Temp2(request):
    return render(request,'customer/temp2.html')

@csrf_exempt   
def Search_by_all(request):
    return render(request,'customer/product_category.html')
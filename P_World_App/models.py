from django.db import models


class Admin_login(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)
    password = models.CharField(max_length=150, null=True, blank=True)


class User_Details(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=450, null=True, blank=True)
    password = models.CharField(max_length=90, null=True, blank=True)
    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length = 100 , null = True , blank = True)
    country_code = models.CharField(max_length=15, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=300, null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)
    bussiness_name = models.CharField(max_length=400, null=True, blank=True)
    bussiness_address = models.CharField(max_length=500, null=True, blank=True)
    map_location = models.CharField(max_length=500, null=True, blank=True)
    latitude = models.CharField(max_length=400, null=True, blank=True)
    longitude = models.CharField(max_length=400, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_image/', null=True, blank=True)
    user_type = models.CharField(max_length=300, null=True, blank=True)
    status = models.BooleanField(default=False)
    created_datetime = models.DateTimeField(null=True, blank=True)
    sign_up_status = models.BooleanField(default=False)
    
    is_profile_create = models.BooleanField(default = False)
    token = models.CharField(max_length=400, null=True, blank=True)


class Set_Availability(models.Model):
    fk_doctor = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True)
    add_shift = models.CharField(max_length=300, null=True, blank=True)
    from_shift = models.TimeField(null=True, blank=True)
    to_shift = models.TimeField(null=True, blank=True)
    select_days = models.CharField(max_length=300, null=True, blank=True)


## Note : Assume pet_type as service_type    
class User_service(models.Model):
    fk_doctor = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    pet_type = models.CharField(max_length=100, null=True, blank=True)
    charges = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateField(auto_now=True, null=True, blank=True)


class New_Pet(models.Model):
    fk_customer = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True)
    pet_name = models.CharField(max_length=250, null=True, blank=True)
    type_of_pet = models.CharField(max_length=500, null=True, blank=True)
    breed = models.CharField(max_length=250, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    age = models.CharField(max_length=25, null=True, blank=True)
    gender = models.CharField(max_length=250, null=True, blank=True)
    weight = models.CharField(max_length=250, null=True, blank=True)
    pet_description = models.TextField(null=True, blank=True)
    pet_image = models.ImageField(upload_to='pet_image/', null=True, blank=True)
    created_datetime = models.DateTimeField(null=True, blank=True)


class Add_Pet_Reminder(models.Model):
    fk_user = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True)
    fk_pet = models.ForeignKey(New_Pet, on_delete=models.CASCADE, null=True, blank=True)
    reminder_name = models.CharField(max_length=250, null=True, blank=True)
    select_date = models.DateField(null=True, blank=True)
    select_time = models.TimeField(null=True, blank=True)
    reminder_status = models.BooleanField(default = True)


class DoctorsAppointment(models.Model):
    doctor = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor')
    client = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='client')
    fk_pet = models.ForeignKey(New_Pet, on_delete=models.CASCADE, null=True, blank=True)
    booking_time = models.TimeField(null=True, blank=True)
    booking_date = models.DateField(null=True, blank=True)
    txn_id = models.CharField(max_length=1000, null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    txn_date = models.DateField(null=True, blank=True)
    txn_time = models.TimeField(null=True, blank=True)
    txn_status = models.CharField(max_length=50, null=True, blank=True)
    payment_method_type = models.CharField(max_length=50, null=True, blank=True)
    book_status = models.CharField(max_length=100, null=True, blank=True)    ## Booked, Cancelled, Completed
    status = models.BooleanField(default=False)
    services = models.CharField(max_length=650, null=True, blank=True)
    services_title = models.CharField(max_length=5000, null=True, blank=True)
    cancelled_by = models.CharField(max_length=100, null=True, blank=True)
    vendor_type = models.CharField(max_length=100, null=True, blank=True)
    review_status = models.BooleanField(default = False)
    time = models.TimeField(auto_now= True)
    date = models.DateField(auto_now=True)
    
class UserLike(models.Model):
    fk_user_sender = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='like_sender')
    fk_user_receiver = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='like_receiver')
    date = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(null=True, blank=True, default=False)




class Notification(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    notification = models.TextField(null=True, blank=True)
    sender = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='sender')
    receiver = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='receiver')
    date = models.DateTimeField(blank=True, null=True)

class CountryMaster(models.Model):
    sortname = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    country_code = models.CharField(max_length=100, null=True, blank=True)
    
class PetMaster(models.Model): 
    name = models.CharField(max_length=100, null=True, blank=True)



class ItemCategoryMaster(models.Model):
    category_name = models.CharField(max_length = 200 , blank = True , null = True)


class ItemMaster(models.Model):
    fk_vendor = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True)
    fk_category = models.ForeignKey(ItemCategoryMaster , on_delete=models.CASCADE , null = True , blank = True)
    item_name = models.CharField(max_length = 200 , blank = True , null = True)
    item_price = models.FloatField(blank = True , null = True, default=0)
    item_image = models.ImageField(upload_to='item_image/', null=True, blank=True)
    pet_type = models.CharField(max_length = 100 , null = True , blank = True)
    available_status = models.BooleanField(default = False)
    item_description = models.TextField(blank = True , null = True)
    
    
class AddtoCart(models.Model):
    fk_b = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='fk_b')
    fk_item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE, null=True, blank=True)
    fk_vendor = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True , related_name='fk_vendor')
    fk_user = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True , related_name='fk_user')
    quantity = models.IntegerField(blank = True , null = True)
    item_price = models.FloatField(blank = True , null = True)
    total_item_price = models.FloatField(blank = True , null = True)
    delivery_charge = models.FloatField(blank = True , null = True)
    taxes = models.FloatField(blank = True , null = True)
    total_amount = models.FloatField(null=True, blank=True)
    
class OrdersTable(models.Model):
    order_no = models.CharField(max_length = 100 , blank = True , null = True)
    fk_business = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='fk_business')
    fk_users = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='fk_users') 
    item_name = models.CharField(max_length=50, null=True, blank=True)
    item_price = models.FloatField(null = True , blank = True)
    total_quantity = models.IntegerField(blank = True , null = True)
    booking_time = models.TimeField(null=True, blank=True)
    booking_date = models.DateField(null=True, blank=True) 
    txn_id = models.CharField(max_length=1000, null=True, blank=True)
    delivery_charge = models.FloatField(blank = True , null = True)
    taxes = models.FloatField(blank = True , null = True)
    discount = models.FloatField(blank = True , null = True)
    total_amount = models.FloatField(null=True, blank=True)
    txn_date = models.DateField(null=True, blank=True)
    txn_time = models.TimeField(null=True, blank=True)
    txn_status = models.CharField(max_length=50, null=True, blank=True)
    payment_method_type = models.CharField(max_length=50, null=True, blank=True)
    order_status = models.CharField(max_length=100, null=True, blank=True)    ### Approved, Pending, Cancelled  
    status = models.BooleanField(default=False)
    cancelled_by = models.CharField(max_length=100, null=True, blank=True) 
    cancelled_reason = models.CharField(max_length=300, null=True, blank=True) 
    review_status = models.BooleanField(default = False)
    delivery_note = models.TextField(blank = True , null = True)
    ## address 
    name = models.CharField(max_length=100,blank=True,null=True)
    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length = 100 , null = True , blank = True)
    country_code = models.CharField(max_length=15, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    address1 = models.CharField(max_length=100,blank=True,null=True)
    address2 = models.CharField(max_length=100,blank=True,null=True)
    province = models.CharField(max_length=100,blank=True,null=True)
    city = models.CharField(max_length=100,blank=True,null=True)
    postalcode = models.CharField(max_length=100,blank=True,null=True)
    
class OrderItemTable(models.Model):
    fk_orders = models.ForeignKey(OrdersTable, on_delete=models.CASCADE, null=True, blank=True)
    fk_item = models.ForeignKey(ItemMaster, on_delete=models.CASCADE, null=True, blank=True)
    fk_vendors = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='fk_vendors')
    fk_busines = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True, related_name='fk_busines')
    item_quantity = models.IntegerField(blank = True , null = True)
    item_price = models.FloatField(blank = True , null = True)
    item_total_price = models.FloatField(blank = True , null = True)
    booking_time = models.TimeField(auto_now = True )
    booking_date = models.DateField( auto_now = True) 
    
   

class UserRatingReview(models.Model):
    fk_order = models.ForeignKey(OrderItemTable, on_delete=models.PROTECT, null=True, blank=True)
    fk_apt = models.ForeignKey(DoctorsAppointment, on_delete=models.CASCADE, null=True, blank=True)
    fk_user_sender = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='rating_sender')
    fk_user_receiver = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='rating_receiver')
    rating = models.FloatField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_datetime = models.DateTimeField(null=True, blank=True, auto_now = True)
    status = models.BooleanField(default=False)


class CityMaster(models.Model):
    city = models.CharField(max_length=100,blank=True,null=True)
    state_id = models.IntegerField(blank= True,null=True)
   
class ProvinceMaster(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    country_id = models.IntegerField(blank= True,null=True)
    
class deliveryAddress(models.Model):
    fk_users = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length = 100 , null = True , blank = True)
    country_code = models.CharField(max_length=15, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    address1 = models.CharField(max_length=100,blank=True,null=True)
    address2 = models.CharField(max_length=100,blank=True,null=True)
    province = models.CharField(max_length=100,blank=True,null=True)
    city = models.CharField(max_length=100,blank=True,null=True)
    postalcode = models.CharField(max_length=100,blank=True,null=True)


class SupportTicket(models.Model):
    user_id = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length = 200 , null = True , blank = True)
    message = models.TextField()
    status = models.CharField(max_length=20, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - User {self.user_id}"
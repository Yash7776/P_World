from django.contrib import admin
from .models import *
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import CityMaster, ProvinceMaster

class User_Details_class(admin.ModelAdmin):
    list_display = ('id', 'name', 'password', 'mobile_no', 'email', 'user_type', 'created_datetime') 
admin.site.register(User_Details, User_Details_class)


class Admin_login_class(admin.ModelAdmin):
    list_display = ('id', 'username', 'password') 
admin.site.register(Admin_login, Admin_login_class)


class Set_Availability_class(admin.ModelAdmin):
    list_display = ('id', 'add_shift', 'fk_doctor', 'from_shift', 'to_shift', 'select_days') 
admin.site.register(Set_Availability, Set_Availability_class)


class User_service_class(admin.ModelAdmin):
    list_display = ('id', 'fk_doctor', 'title', 'description', 'pet_type', 'charges', 'created_at') 
admin.site.register(User_service, User_service_class)


class New_Pet_class(admin.ModelAdmin):
    list_display = (
        'id', 'fk_customer', 'pet_name', 'type_of_pet', 'breed', 'birth_date', 'gender', 'weight', 'pet_image', 'created_datetime') 
admin.site.register(New_Pet, New_Pet_class)


class Add_Pet_Reminder_class(admin.ModelAdmin):
    list_display = ('id', 'reminder_name', 'select_date', 'select_time') 
admin.site.register(Add_Pet_Reminder, Add_Pet_Reminder_class)


class DoctorsAppointment_class(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'client', 'booking_time', 'booking_date', 'amount','book_status','vendor_type') 
admin.site.register(DoctorsAppointment, DoctorsAppointment_class)


class UserLike_class(admin.ModelAdmin):
    list_display = ('id', 'fk_user_sender', 'fk_user_receiver', 'date') 
admin.site.register(UserLike, UserLike_class)


class UserRatingReview_class(admin.ModelAdmin):
    list_display = ('id', 'fk_user_sender', 'fk_user_receiver', 'rating', 'comment', 'created_datetime') 
admin.site.register(UserRatingReview, UserRatingReview_class)


class Notification_class(admin.ModelAdmin):
    list_display = ('id', 'title', 'notification', 'sender', 'receiver', 'date') 
admin.site.register(Notification, Notification_class)

# @admin.register(CountryMaster)
# class CountryMasterAdmin(admin.ModelAdmin):
#     list_display = ['id','sortname','name','country_code']

@admin.register(CountryMaster)
class CountryMasterAdmin(ImportExportModelAdmin):
    list_display = ['id','sortname','name','country_code']
    list_per_page = 20

    
@admin.register(PetMaster)
class PetMasterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name' ]
    

@admin.register(ItemCategoryMaster)
class PetMasterAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name' ]
    

@admin.register(MasterItem)
class MasterItemAdmin(admin.ModelAdmin):
    list_display = [
        'item_name',           # was ap_item_name
        'fk_category',         # was ap_fk_category
        'pet_type',            # was ap_pet_type
        'available_status',    # was ap_available_status
        'created_at',
        'updated_at',
    ]

@admin.register(StoreItem)
class PetMasterAdmin(admin.ModelAdmin):  # ← consider renaming class to StoreItemAdmin
    list_display = [
        'get_store_name',       # we'll define this
        'get_master_item_name', # we'll define this
        'item_price',
        'get_category',         # optional
        'get_pet_type',         # optional
    ]
    list_filter = ['fk_store', 'fk_master__fk_category']
    search_fields = ['fk_master__item_name', 'fk_store__username']  # adjust according to User_Details fields

    # Helper methods (these fix the "not a field" problem)
    @admin.display(description='Store / Vendor')
    def get_store_name(self, obj):
        return obj.fk_store.user_name if obj.fk_store else '-'

    @admin.display(description='Item Name')
    def get_master_item_name(self, obj):
        return obj.fk_master.item_name if obj.fk_master else '-'

    @admin.display(description='Category')
    def get_category(self, obj):
        return obj.fk_master.fk_category if obj.fk_master and obj.fk_master.fk_category else '-'

    @admin.display(description='Pet Type')
    def get_pet_type(self, obj):
        return obj.fk_master.pet_type if obj.fk_master else '-'

@admin.register(AddtoCart)
class AddtoCartAdmin(admin.ModelAdmin):
    list_display = ['id','fk_item','fk_vendor','fk_user','quantity','item_price','total_item_price']
    





@admin.register(CityMaster)
class CityMasterAdmin(ImportExportModelAdmin):
    list_display = ['id', 'city', 'state_id']
    list_per_page = 20


@admin.register(ProvinceMaster)
class ProvinceMasterAdmin(ImportExportModelAdmin):
    list_display = ['id', 'name', 'country_id']
    list_per_page = 20


@admin.register(deliveryAddress)
class deliveryAddressAdmin(admin.ModelAdmin):
    list_display = [field.name for field in deliveryAddress._meta.get_fields()]
    

@admin.register(OrdersTable)
class OrderTableAdmin(admin.ModelAdmin):
    list_display = ['id','order_no','fk_users','fk_business','item_name','item_price','total_quantity','booking_date','discount','total_amount','order_status','status' ]
    

@admin.register(OrderItemTable)
class OrderItemTableAdmin(admin.ModelAdmin):
    list_display = ['id','fk_orders','fk_item','fk_vendors','item_quantity','item_price','item_total_price']
 

 
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id','status','category','created_at']



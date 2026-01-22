from rest_framework import serializers
from .models import *


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Details
        fields = '__all__'  # for all fields

    def __init__(self, *args, **kwargs):
        super(UserDetailSerializer, self).__init__(*args, **kwargs)


class UserDetailSerializer1(serializers.ModelSerializer):
    DEFAULT_LATITUDE = "21.118064"
    DEFAULT_LONGITUDE = "79.0450328"

    class Meta:
        model = User_Details
        fields = [
            'id',
            'name',
            'email',
            'mobile_no',
            'map_location',
            'address',
            'latitude',
            'longitude',
            'profile_image'
        ]

    def validate(self, attrs):
        """
        Handle empty / null latitude & longitude safely
        """

        lat = attrs.get('latitude')
        lng = attrs.get('longitude')

        if not lat or str(lat).strip() == "":
            attrs['latitude'] = self.DEFAULT_LATITUDE

        if not lng or str(lng).strip() == "":
            attrs['longitude'] = self.DEFAULT_LONGITUDE

        return attrs



class SetAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Set_Availability
        fields = '__all__'  # for all fields

    def __init__(self, *args, **kwargs):
        super(SetAvailabilitySerializer, self).__init__(*args, **kwargs)


class DoctorServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_service
        fields = '__all__'  # for all fields

    def __init__(self, *args, **kwargs):
        super(DoctorServiceSerializer, self).__init__(*args, **kwargs)


class AddNewPetSerializer(serializers.ModelSerializer):
    class Meta:
        model = New_Pet
        fields = '__all__'  # for all fields

    def __init__(self, *args, **kwargs):
        super(AddNewPetSerializer, self).__init__(*args, **kwargs)


class DoctorsAppointmentSerializer(serializers.ModelSerializer):
    fk_pet = AddNewPetSerializer(read_only=True)
    doctor = UserDetailSerializer1(read_only=True)
    client = UserDetailSerializer1(read_only=True)

    #### fk_pet = serializers.StringRelatedField()
    #### doctor = serializers.StringRelatedField()
    #### client = serializers.StringRelatedField()
    class Meta:
        model = DoctorsAppointment
        fields = '__all__'  # for all fields
        depth = 1

    def create(self, validated_data):
        validated_data['fk_pet'] = self.context['fk_pet']
        validated_data['doctor'] = self.context['doctor']
        validated_data['client'] = self.context['client']
        obj = DoctorsAppointment.objects.create(**validated_data)  # saving post object
        return obj

    def __init__(self, *args, **kwargs):
        super(DoctorsAppointmentSerializer, self).__init__(*args, **kwargs)


class UserLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLike
        fields = '__all__'  # for all fields

    def __init__(self, *args, **kwargs):
        super(UserLikeSerializer, self).__init__(*args, **kwargs)


class UserRatingReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRatingReview
        fields = '__all__'

    def __int__(self, *args, **kwargs):
        super(UserRatingReviewSerializer, self).__int__(*args, **kwargs)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

    def __int__(self, *args, **kwargs):
        super(NotificationSerializer, self).__int__(*args, **kwargs)
        
class AddtoCartSerializer(serializers.ModelSerializer):
    class Meta:
            model = AddtoCart
            fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AddtoCartSerializer, self).__init__(*args, **kwargs)
        
        
class countrySerializer(serializers.ModelSerializer):
    class Meta:
            model = CountryMaster
            fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(countrySerializer, self).__init__(*args, **kwargs)
        
        
class provinceSerializer(serializers.ModelSerializer):
    class Meta:
            model = ProvinceMaster
            fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(provinceSerializer, self).__init__(*args, **kwargs)

        
class citySerializer(serializers.ModelSerializer):
    class Meta:
            model = CityMaster
            fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(citySerializer, self).__init__(*args, **kwargs)


class PetMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetMaster
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(PetMasterSerializer, self).__init__(*args, **kwargs)


class ItemCatMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategoryMaster
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(ItemCatMasterSerializer, self).__init__(*args, **kwargs)
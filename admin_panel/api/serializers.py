from rest_framework.serializers import(
	 ModelSerializer,
	 ValidationError,
	 SerializerMethodField,
	 
	 )

from django.contrib.auth.models import User 
from designer_stylist.models import *
from product.models import CouponCode

from accounts.models import UserOtherInfo

class StylistDesignerCategorySerializer(ModelSerializer):

	class Meta:
		model = StylistDesignerCategory
		fields = ['name']

class CouponSerializer(ModelSerializer):
	class Meta:
		model = CouponCode
		fields = '__all__'

class UserSerializer(ModelSerializer):

	class Meta:
		model = User
		fields = ['id','first_name','last_name','email']



class UserOtherInfoSerializer(ModelSerializer):
	user  = SerializerMethodField()

	def get_user(self ,instance):
		return UserSerializer(instance.user).data


	class Meta:
		model = UserOtherInfo
		fields = ['id' , 'user' , 'phonenum']
from rest_framework.serializers import(
	 ModelSerializer,
	 ValidationError,
	 SerializerMethodField,
	 
	 )
from designer_stylist.models import * 
from datetime import datetime
from django.utils import timezone
from product.models import Product,ProductAvailableSize,ProductAvailableColour,ProductReviews
from product.api.serializers import ProductDetailSerializer,ProductListSerializer
from django.db.models import Q	
from django.db.models import Count, F, Value


class DesignerImagesSerializer(ModelSerializer):
	class Meta:
		model = Image
		fields= ['image']


class DesignerAchievementSerializer(ModelSerializer):
	achievent_images     = SerializerMethodField()

	def get_achievent_images(self,instance):
		qs = 	Image.objects.filter(achievement = instance.id)
		data =	DesignerImagesSerializer(qs,many=True).data
		return data
	
	class Meta:
		model = Achievement
		fields = [

			'title',
			'year',
			'about',
			'achievent_images',


		]



class DesignerListSerializer(ModelSerializer):
	class Meta:
		model = Profile
		fields = '__all__'


class StylistListSerializer(ModelSerializer):
	class Meta:
		model = Profile
		fields = '__all__'


class StylistDesignerSectionSerializer(ModelSerializer):
	class Meta:
		model = StylistDesignerSection
		fields  ='__all__'


class DesignerDetailSerializer(ModelSerializer):
	achievement = SerializerMethodField()

	collections = SerializerMethodField()

	def get_achievement(self,instance):
		qs = 	Achievement.objects.filter(designerprofile = instance.id).first()
		data =	DesignerAchievementSerializer(qs).data
		return data

	def get_collections(self,instance):
		sec_qs = StylistDesignerSection.objects.filter(user=instance.user)
		section_data = []
		count=0
		for sec_obj in sec_qs:
			
			product_qs	 =	Product.objects.filter(user = instance.user, active=True, is_deleted=False,  usersection=sec_obj)
			if product_qs.count() >=1:
				section_data.append(StylistDesignerSectionSerializer(sec_obj).data)
				product_data = ProductListSerializer(product_qs,many=True).data
				section_data[count]['products']=product_data
				count = count + 1
			
		return section_data

	class Meta:
		model = Profile
		fields =[
			'id',
			'name',
			'email',
			'role',
			'profileimg',
			'coverimg',
			'achievement',
			'collections'


		]


class DesignerDetailHelperSerializer(ModelSerializer):

	class Meta:
		model = Profile
		fields =[
			'id',
			'name',
			'email',
			'role',
			'profileimg',
			'coverimg',

		]
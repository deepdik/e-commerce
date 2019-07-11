from rest_framework.generics import (
		CreateAPIView,
		ListAPIView
	)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
	HTTP_200_OK,
	HTTP_400_BAD_REQUEST
	,HTTP_204_NO_CONTENT,
	HTTP_201_CREATED,
	HTTP_500_INTERNAL_SERVER_ERROR,
	HTTP_404_NOT_FOUND
	)

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
import django_filters

from designer_stylist.models import * 
from .serializers import *
from product.models import *
from product.api.serializers import CategoryListFilterSeializer,SubCategoryListFilterSeializer,SubSubCategoryListFilterSeializer,ProductAvailableColourSerializer


class DesignerListAPIView(APIView):
	def get(self, request, *args, **kwargs):
		qs = Profile.objects.filter(role=3).order_by('name')
		data = DesignerListSerializer(qs, many=True).data
		return Response({
				'message':'success',
				'designer':data
				},status=HTTP_200_OK)


class DesignerDetailAPIView(APIView):
	def get(self, request, *args, **kwargs):
		designer_id = self.kwargs['designer_id']
		try:
			obj = Profile.objects.get(role=3,id = designer_id )
		except:
			return Response({
				'message':'No content found'
				},status=HTTP_404_NOT_FOUND)

		serializer = DesignerDetailSerializer(obj)
		return Response({
					'message':'success',
					'designer':serializer.data
					},status=HTTP_200_OK)

			# return Response({
			# 	'message':'No content found'
			# 	},status=HTTP_404_NOT_FOUND)

class StylistListAPIView(APIView):
	def get(self, request, *args, **kwargs):
		qs = Profile.objects.filter(role=4).order_by('name')
		data = StylistListSerializer(qs, many=True).data
		return Response({
				'message':'success',
				'stylist':data
				},status=HTTP_200_OK)


class StylistDetailAPIView(APIView):
	def get(self, request, *args, **kwargs):
		stylist_id = self.kwargs['stylist_id']
		try:
			obj = Profile.objects.select_related('user').get(role=4, id = stylist_id)
			data = DesignerDetailSerializer(obj).data
			return Response({
				'message':'success',
				'stylist':data
				},status=HTTP_200_OK)

		except:
			return Response({
				'message':'No content found'
				},status=HTTP_404_NOT_FOUND)


class ProductListAPIView(APIView):

	def get(self, request, *args, **kwargs):
		profile_id = self.kwargs['profile_id']
		try:
			obj = Profile.objects.select_related('user').get(id = profile_id)
		except:			
			return Response({
				'message':'No content found'
				},status=HTTP_404_NOT_FOUND)

		profile_detail = DesignerDetailSerializer(obj).data
		sortby = request.GET.get('sort_by')
		user = obj.user

		if sortby is not None and int(sortby) < 6:
			print('ok')
			if sortby == "1":
				sortby='-qty_sold'
			elif sortby == "2":
				sortby = '-created_date'
			elif sortby == "3":
				sortby = '-avg_rating'
			elif sortby == "4":
				sortby ='min_price'
			elif sortby == "5":
				sortby = '-min_price'
			
			qs = Product.objects.filter(active=True, is_deleted=False, user=user).select_related('category','subcategory','subsubcategory').prefetch_related('available_colours').order_by(sortby)
			data = ProductListSerializer(qs, many=True).data

			filters = {}

			# owncategories = StylistDesignerCategory.objects.filter(user=user).values('name','id')
			# filters['categories'] = owncategories

			sizes = [{'size':'XS'},{'size':'S'},{'size':'M'},{'size':'L'},{'size':'XL'},{'size':'XXL'},{'size':'XXXL'}]
			filters['sizes'] = sizes

			# colours = 	qs.exclude(colour__isnull=True).values('colour__colour').distinct()
			# filters['colours'] = colours

			material = qs.values('material').exclude(material__isnull=True).distinct()
			filters['material'] = material

			usersection = StylistDesignerSection.objects.filter(user=user).values('name','id')
			filters['usersection'] = usersection

			fit = qs.values('fit').exclude(fit__isnull=True).distinct()
			filters['fit'] = fit

			price = [{'price':'100-500'},{'price':'500-1000'},{'price':'1000-5000'},
			{'price':'above-5000'}]

			filters['price'] = price

			offers = [{'id':10,'offer':'10 and above'},{'id':20,'offer':'20 and above'},{'id':30,'offer':'30 and above'},
			{'id':40,'offer':'40 and above'},{'id':50,'offer':'50 and above'},{'id':60,'offer':'60 and above'}]
			{'id':70,'offer':'70 and above'}

			filters['offers'] = offers

			category_list = set(qs.values_list('category' ,flat=True))
			subcategory_list = set(qs.values_list('subcategory' ,flat=True))
			subsubcategory_list = set(qs.values_list('subsubcategory' ,flat=True))
			cat_qs = Category.objects.filter(id__in = category_list, active=True,)

			cat_data = CategoryListFilterSeializer(cat_qs ,many=True).data
			cat_count = 0
			for cat_obj in cat_qs:
				sub_qs = SubCategory.objects.filter(category=cat_obj , active=True, id__in = subcategory_list)
				subcat_data =  SubCategoryListFilterSeializer(sub_qs, many=True).data
				subcat_count =0
				cat_data[cat_count]['subcategory'] = subcat_data
				for sub_obj in sub_qs:
					subsubcat_qs = SubSubCategory.objects.filter(category = cat_obj , active=True, subcategory=sub_obj, id__in = subsubcategory_list )
					subsubcat_data =SubSubCategoryListFilterSeializer(subsubcat_qs,many=True).data
					cat_data[cat_count]['subcategory'][subcat_count]['subsubcategory'] = subsubcat_data
					subcat_count = subcat_count+1
				cat_count = cat_count +1

			filters['categories'] =cat_data 

			
			return Response({
				'message':'success',
				'products':data,
				'filters':filters,
				'profile_detail':profile_detail
					
				},status=HTTP_200_OK)

		filters = request.GET.get('filter')




		qs = Product.objects.filter(active=True, is_deleted=False ,user=user).select_related('category','subcategory','subsubcategory').prefetch_related('available_colours')
		data = ProductListSerializer(qs, many=True).data


		filters = {}

		# owncategories = StylistDesignerCategory.objects.filter(user=user).values('name','id')
		# filters['categories'] = owncategories

		sizes = [{'size':'XS'},{'size':'S'},{'size':'M'},{'size':'L'},{'size':'XL'},{'size':'XXL'},{'size':'XXXL'}]
		filters['sizes'] = sizes

		# colours = 	qs.exclude(colour__isnull=True).values('colour__colour').distinct()
		# filters['colours'] = colours

		material = qs.values('material').exclude(material__isnull=True).distinct()
		filters['material'] = material

		fit = qs.values('fit').exclude(fit__isnull=True).distinct()
		filters['fit'] = fit

		usersection = StylistDesignerSection.objects.filter(user=user).values('name','id')
		filters['usersection'] = usersection


		price = [{'price':'100-500'},{'price':'500-1000'},{'price':'1000-5000'},
		{'price':'above-5000'}]

		filters['price'] = price

		offers = [{'id':10,'offer':'10 and above'},{'id':20,'offer':'20 and above'},{'id':30,'offer':'30 and above'},
		{'id':40,'offer':'40 and above'},{'id':50,'offer':'50 and above'},{'id':60,'offer':'60 and above'}]
		{'id':70,'offer':'70 and above'}

		filters['offers'] = offers

		category_list = set(qs.values_list('category' ,flat=True))
		subcategory_list = set(qs.values_list('subcategory' ,flat=True))
		subsubcategory_list = set(qs.values_list('subsubcategory' ,flat=True))
		cat_qs = Category.objects.filter(id__in = category_list,active=True,)

		cat_data = CategoryListFilterSeializer(cat_qs ,many=True).data
		cat_count = 0
		for cat_obj in cat_qs:
			sub_qs = SubCategory.objects.filter(category=cat_obj , active=True, id__in = subcategory_list)
			subcat_data =  SubCategoryListFilterSeializer(sub_qs, many=True).data
			subcat_count =0
			cat_data[cat_count]['subcategory'] = subcat_data
			for sub_obj in sub_qs:
				subsubcat_qs = SubSubCategory.objects.filter(category = cat_obj , active=True,subcategory=sub_obj, id__in = subsubcategory_list )
				subsubcat_data =SubSubCategoryListFilterSeializer(subsubcat_qs,many=True).data
				cat_data[cat_count]['subcategory'][subcat_count]['subsubcategory'] = subsubcat_data
				subcat_count = subcat_count+1
			cat_count = cat_count +1

		filters['categories'] =cat_data 

		return Response({
				'message':'success',
				'products':data,
				'filters':filters,
	
				'profile_detail':profile_detail,
					
				},status=HTTP_200_OK)


class CustomFilterList(django_filters.Filter):
	def filter(self, qs, value):
		if value not in (None, ''):
			values = [v for v in value.split(',')]
			print(values)
			if '' in values:
				values.remove('')
			return qs.filter(**{'%s__%s' % (self.field_name, self.lookup_expr): values})
		return qs


class CustomColourFilter(django_filters.Filter):
	def filter(self, qs, value):
		if value not in (None, ''):
			values = [v for v in value.split(',')]
			print(values)
			if '' in values:
				values.remove('')
			return qs.filter(available_colours__colour__in = values, available_colours__is_active=True)
		return qs 


class CustomSizeFilter(django_filters.Filter):
	def filter(self, qs, value):
		if value not in (None, ''):
			values = [v for v in value.split(',')]
			print(values)
			if '' in values:
				values.remove('')
			return qs.filter(available_colours__size_and_qty__size__in = values,  available_colours__is_active=True, available_colours__is_out_of_stock = False ,available_colours__size_and_qty__available_qty__gt = 0)
		return qs 


class ProductFilter(django_filters.FilterSet):
	
	price = django_filters.RangeFilter(field_name='min_price') # single option
	material = CustomFilterList(lookup_expr="in") # multiple
	fit = CustomFilterList(lookup_expr="in" ) # multiple
	offer = django_filters.NumberFilter(field_name='offer_of_min', lookup_expr='gt') # single option
	usersection = CustomFilterList(field_name='usersection', lookup_expr="in") # multiple
	category = CustomFilterList(field_name='category', lookup_expr="in") # multiple
	subcategory = CustomFilterList(field_name='subcategory', lookup_expr="in") # multiple
	subsubcategory = CustomFilterList(field_name='subsubcategory', lookup_expr="in") # multiple
	colour = CustomColourFilter(field_name='available_colours__colour', lookup_expr="in") # multiple
	size = CustomSizeFilter(field_name="available_colours__size_and_qty__size", lookup_expr="in") # multiple

	class Meta:
		model = Product
		fields = {'category','subcategory','subsubcategory', 'usersection','price','material','fit','offer' ,'colour','size'}


class StylistDesignerProductFilterList(ListAPIView):
	serializer_class = ProductListSerializer
	filter_backends = (DjangoFilterBackend,)
	filterset_class = ProductFilter

	def get_queryset(self):
		profile_id = self.kwargs['profile_id']
		obj = Profile.objects.select_related('user').get(id = profile_id)

		queryset = Product.objects.filter(active=True, is_deleted=False ,user=obj.user).select_related('category','subcategory','subsubcategory').prefetch_related('available_colours').distinct().order_by('-qty_sold')
		
		return queryset

	def list(self, request, *args, **kwargs):
		response = super().list(request, *args, **kwargs)

		profile_id = self.kwargs['profile_id']

		obj = Profile.objects.select_related('user').get(id = profile_id)

		qs = Product.objects.filter(active=True, is_deleted=False ,user=obj.user).select_related('category','subcategory','subsubcategory')
		data = ProductListSerializer(qs, many=True).data

		filters = {}
		# owncategories = StylistDesignerCategory.objects.filter(user=obj.user).values('name','id')
		# filters['categories'] = owncategories

		sizes = [{'size':'XS'},{'size':'S'},{'size':'M'},{'size':'L'},{'size':'XL'},{'size':'XXL'},{'size':'XXXL'}]
		filters['sizes'] = sizes

		# colours = qs.exclude(available_colours__isnull=True).annotate(name=F('available_colours__colour__')).values('name','available_colours__colour__id','available_colours__colour__colour_code').distinct()
		# filters['colours'] = colours

		material = qs.values('material').exclude(material__isnull=True).distinct()
		filters['material'] = material

		fit = qs.values('fit').exclude(fit__isnull=True).distinct()
		filters['fit'] = fit

		usersection = StylistDesignerSection.objects.filter(user=obj.user).values('name','id')
		filters['usersection'] = usersection

		price = [{'price':'100-500'},{'price':'500-1000'},{'price':'1000-5000'},
		{'price':'above-5000'}]

		filters['price'] = price

		offers = [{'id':10,'offer':'10 and above'},{'id':20,'offer':'20 and above'},{'id':30,'offer':'30 and above'},
		{'id':40,'offer':'40 and above'},{'id':50,'offer':'50 and above'},{'id':60,'offer':'60 and above'}]
		{'id':70,'offer':'70 and above'}

		filters['offers'] = offers
		category_list = set(qs.values_list('category' ,flat=True))
		subcategory_list = set(qs.values_list('subcategory' ,flat=True))
		subsubcategory_list = set(qs.values_list('subsubcategory' ,flat=True))
		cat_qs = Category.objects.filter(id__in = category_list, active=True,)

		cat_data = CategoryListFilterSeializer(cat_qs ,many=True).data
		cat_count = 0
		for cat_obj in cat_qs:
			sub_qs = SubCategory.objects.filter(category=cat_obj , active=True, id__in = subcategory_list)
			subcat_data =  SubCategoryListFilterSeializer(sub_qs, many=True).data
			subcat_count =0
			cat_data[cat_count]['subcategory'] = subcat_data
			for sub_obj in sub_qs:
				subsubcat_qs = SubSubCategory.objects.filter(category = cat_obj , active=True,subcategory=sub_obj, id__in = subsubcategory_list )
				subsubcat_data =SubSubCategoryListFilterSeializer(subsubcat_qs,many=True).data
				cat_data[cat_count]['subcategory'][subcat_count]['subsubcategory'] = subsubcat_data
				subcat_count = subcat_count+1
			cat_count = cat_count +1

		filters['categories'] =cat_data 

		return Response({'products':response.data,
							'filters':filters})


from rest_framework.filters import SearchFilter, OrderingFilter

class StylistDesignerProductListWebView(ListAPIView):
	serializer_class = ProductListSerializer
	filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
	filterset_class = ProductFilter
	# filter_fields = ('category','subcategory')
	ordering_fields = ('qty_sold','created_date','avg_rating','min_price')
	search_fields = ('category__cat_name','subcategory__subcat_name','subsubcategory__subsubcat_name',
		'name','brand','material','fit')
	
	def get_queryset(self):
		profile_id = self.kwargs['profile_id']
		obj = Profile.objects.select_related('user').get(id = profile_id)

		queryset = Product.objects.filter(active=True,is_deleted=False ,user=obj.user).select_related('category','subcategory','subsubcategory').prefetch_related('available_colours').distinct()
		
		return queryset


	def list(self, request, *args, **kwargs):
		response = super().list(request, *args, **kwargs)
		print(response)
		qs = self.get_queryset()
		obj = Profile.objects.select_related('user').get(id = self.kwargs['profile_id'])
		profile_detail = DesignerDetailSerializer(obj).data

		# qs = Product.objects.filter(active=True,user=obj.user).select_related('category','subcategory','subsubcategory')
		# data = ProductListSerializer(qs, many=True).data

		filters = {}
		# owncategories = StylistDesignerCategory.objects.filter(user=obj.user).values('name','id')
		# filters['categories'] = owncategories

		sizes = [{'size':'XS'},{'size':'S'},{'size':'M'},{'size':'L'},{'size':'XL'},{'size':'XXL'},{'size':'XXXL'}]
		filters['sizes'] = sizes


		colours = qs.exclude(available_colours__isnull=True, available_colours__is_active=False).values( colour_id = F('available_colours__colour__id'),colour_name = F('available_colours__colour__name'),colour_code = F('available_colours__colour__colour_code')).distinct()
		filters['colours'] = colours

		# material = qs.values('material').exclude(material__isnull=True).distinct()
		# filters['material'] = material

		# fit = qs.values('fit').exclude(fit__isnull=True).distinct()
		# filters['fit'] = fit

		# usersection = StylistDesignerSection.objects.filter(user=obj.user).values('name','id')
		# filters['usersection'] = usersection

		price = [{'price':'100-500'},{'price':'500-1000'},{'price':'1000-5000'},
		{'price':'above-5000'}]

		filters['price'] = price

		offers = [{'id':10,'offer':'10 and above'},{'id':20,'offer':'20 and above'},{'id':30,'offer':'30 and above'},
		{'id':40,'offer':'40 and above'},{'id':50,'offer':'50 and above'},{'id':60,'offer':'60 and above'}]
		{'id':70,'offer':'70 and above'}

		filters['offers'] = offers
		category_list = set(qs.values_list('category' ,flat=True))
		subcategory_list = set(qs.values_list('subcategory' ,flat=True))
		subsubcategory_list = set(qs.values_list('subsubcategory' ,flat=True))
		cat_qs = Category.objects.filter(id__in = category_list, active=True,)

		cat_data = CategoryListFilterSeializer(cat_qs ,many=True).data
		cat_count = 0
		for cat_obj in cat_qs:
			sub_qs = SubCategory.objects.filter(category=cat_obj , active=True, id__in = subcategory_list)
			subcat_data =  SubCategoryListFilterSeializer(sub_qs, many=True).data
			subcat_count =0
			cat_data[cat_count]['subcategory'] = subcat_data
			for sub_obj in sub_qs:
				subsubcat_qs = SubSubCategory.objects.filter(category = cat_obj , active=True,subcategory=sub_obj, id__in = subsubcategory_list )
				subsubcat_data =SubSubCategoryListFilterSeializer(subsubcat_qs,many=True).data
				cat_data[cat_count]['subcategory'][subcat_count]['subsubcategory'] = subsubcat_data
				subcat_count = subcat_count+1
			cat_count = cat_count +1

		filters['categories'] =cat_data 

		return Response({'products':response.data,
							'filters':filters,
							'profile_detail':profile_detail
							})



class ProductDetailAPIView(APIView):
	def get(self,request,*args,**kwargs):
		product_id = self.kwargs['product_id']
		profile_id = self.kwargs['profile_id']
		try:
			profile = Profile.objects.select_related('user').get(id = profile_id)
			profile_data = DesignerDetailHelperSerializer(profile).data

			best_selling = Product.objects.filter(is_deleted=False ,user = profile.user).select_related('category','subcategory','subsubcategory').exclude(id=product_id).order_by('-qty_sold')[:10]
			best_selling_data = ProductListSerializer(best_selling ,many=True).data
			obj = Product.objects.select_related('category','subcategory','subsubcategory').prefetch_related('available_colours').get(id=product_id, active=True)
			data = ProductDetailSerializer(obj,context={'request':request}).data
			return Response({
				'product_detail':data,
				'profile_data':profile_data,
				'best_selling':best_selling_data
				},
				status=HTTP_200_OK)

		except:
			return Response({
				'message':'No content Found'

				},
				status=HTTP_404_NOT_FOUND
				)


class ProductDetailByColourAPIView(APIView):
	def get(self,request,*args,**kwargs):
		product_id = self.kwargs['product_id']
		profile_id = self.kwargs['profile_id']
		colour_id = self.kwargs['colour_id']
		

		profile = Profile.objects.select_related('user').get(id = profile_id)
		profile_data = DesignerDetailHelperSerializer(profile).data

		obj = Product.objects.select_related('category','subcategory','subsubcategory').prefetch_related('available_colours').get(id=product_id, active=True)
		data = ProductDetailSerializer(obj, context={'colour_id':colour_id,'request':request}).data

		best_selling = Product.objects.filter(user = profile.user).select_related('category','subcategory','subsubcategory').exclude(id=product_id).order_by('-qty_sold')[:10]
		best_selling_data = ProductListSerializer(best_selling ,many=True).data


		return Response({
				'product_detail':data,
				'profile_data':profile_data,
				'best_selling':best_selling_data
				},
				status=HTTP_200_OK)
		

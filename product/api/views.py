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
from django.contrib.auth import get_user_model
from product.models import * 
from designer_stylist.models import *
from .serializers import *


from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
import django_filters


from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication


class CategoryListAPIView(ListAPIView):
	serializer_class 	= CategoryListSeializer

	def get(self,request):
		return Category.objects.filter(active=True)


class SubCategoryListAPIView(ListAPIView):
	serializer_class 	= SubCategoryListSeializer

	def get_queryset(self):
		cat_id = self.kwargs['cat_id']
		qs = SubCategory.objects.filter(active=True,category=cat_id)
		return qs
		

class SubSubCategoryListAPIView(ListAPIView):
	serializer_class 	= SubSubCategoryListSeializer
	def get_queryset(self):
		cat_id = self.kwargs['cat_id']
		subcat_id = self.kwargs['subcat_id']
		qs = SubSubCategory.objects.filter(active=True,subcategory=subcat_id,category=cat_id)
		return qs


# class ProductListAPIView(APIView):


# 	def get(self,*args,**kwargs):
# 		cat_id = self.kwargs['cat_id']
# 		subcat_id = self.kwargs['subcat_id']
# 		subsubcat_id = self.kwargs['subsubcat_id']
# 		qs = Product.objects.filter(subcategory=subcat_id,category=cat_id,subsubcategory=subsubcat_id,active=True)
# 		data = ProductListSerializer(qs,many=True).data
# 		return Response(data,status=HTTP_200_OK)


# from rest_framework.pagination import (
# 	LimitOffsetPagination,
# 	PageNumberPagination

# 	)
from designer_stylist.api.views import ProductFilter

class ProductListAPIView(ListAPIView):
	serializer_class = ProductListSerializer
	filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
	filterset_class = ProductFilter
	# filter_fields = ('category','subcategory')
	ordering_fields = ('qty_sold','created_date','avg_rating','min_price')
	search_fields = ('category__cat_name','subcategory__subcat_name','subsubcategory__subsubcat_name',
		'name','brand','material','fit')


	def get_queryset(self,*args,**kwargs):
		cat_id = self.kwargs['cat_id']
		subcat_id = self.kwargs['subcat_id']
		subsubcat_id = self.kwargs['subsubcat_id']
		qs = Product.objects.filter(subcategory=subcat_id,category=cat_id,subsubcategory=subsubcat_id, active=True, is_deleted = False).distinct()
		# data = ProductListSerializer(qs,many=True).data
		return qs


	def list(self, request, *args, **kwargs):
		response = super().list(request, *args, **kwargs)
		print(response)
		qs = self.get_queryset()
		# qs = Product.objects.filter(active=True,user=obj.user).select_related('category','subcategory','subsubcategory')
		# data = ProductListSerializer(qs, many=True).data

		filters = {}
		# owncategories = StylistDesignerCategory.objects.filter(user=obj.user).values('name','id')
		# filters['categories'] = owncategories

		sizes = [{'size':'XS'},{'size':'S'},{'size':'M'},{'size':'L'},{'size':'XL'},{'size':'XXL'},{'size':'XXXL'}]
		filters['sizes'] = sizes

		colours = qs.exclude(available_colours__isnull=True).values( colour_id = F('available_colours__colour__id'),colour_name = F('available_colours__colour__name'),colour_code = F('available_colours__colour__colour_code')).distinct()
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
							'filters':filters})




class SearchProducts(ListAPIView):
	# pagination_class = PageNumberPagination
	serializer_class = ProductListSerializer
	filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
	# filter_fields = ('category','subcategory')
	# ordering_fields = ('likes','shopName')
	search_fields = ('category__cat_name','subcategory__subcat_name','subsubcategory__subsubcat_name',
		'name','brand','material','fit')

	def get_queryset(self,*args,**kwargs):
		qs = Product.objects.filter(active=True)
		return qs


class SearchProductsWeb(ListAPIView):
	# pagination_class = LimitOffsetPagination
	serializer_class = ProductListSerializer
	filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
	filterset_class = ProductFilter
	# filter_fields = ('category','subcategory')
	ordering_fields = ('qty_sold','created_date','avg_rating','min_price')
	search_fields = ('category__cat_name','subcategory__subcat_name','subsubcategory__subsubcat_name',
		'name','brand','material','fit')

	def get_queryset(self,*args,**kwargs):
		qs = Product.objects.filter(active=True,is_deleted=False).select_related('category','subcategory','subsubcategory').distinct()
		return qs

	def list(self, request, *args, **kwargs):
		response = super().list(request, *args, **kwargs)
		print(response)
		qs = self.get_queryset()
		# qs = Product.objects.filter(active=True,user=obj.user).select_related('category','subcategory','subsubcategory')
		# data = ProductListSerializer(qs, many=True).data

		filters = {}
		# owncategories = StylistDesignerCategory.objects.filter(user=obj.user).values('name','id')
		# filters['categories'] = owncategories

		sizes = [{'size':'XS'},{'size':'S'},{'size':'M'},{'size':'L'},{'size':'XL'},{'size':'XXL'},{'size':'XXXL'}]
		filters['sizes'] = sizes

		colours = qs.exclude(available_colours__isnull=True, available_colours__is_active = False).values( colour_id = F('available_colours__colour__id'),colour_name = F('available_colours__colour__name'),colour_code = F('available_colours__colour__colour_code')).distinct()
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
							'filters':filters})



class ProductDetailAPIView(APIView):
	def get(self,request,*args,**kwargs):
		product_id = self.kwargs['product_id']
		
		obj = Product.objects.select_related('category','subcategory','subsubcategory').prefetch_related('available_colours').filter(id=product_id, active=True, is_deleted=False)
		print(obj)
		if obj.exists():
			data = ProductDetailSerializer(obj.first(),context={'request':request}).data
			return Response(data,status=HTTP_200_OK)
		
		return Response({
			'message':'No data Found'

			},
			status=HTTP_404_NOT_FOUND
			)


class GetDetailOfProductByColourAPIView(APIView):
	def get(self,request,*args,**kwargs):
		product_id = self.kwargs['product_id']
		colour_id = self.kwargs['id']

		prod_obj = Product.objects.get(id =product_id)
		colour_obj = prod_obj.available_colours.get(id=colour_id)
		data =  DetailColourSizeImageSerializer(colour_obj).data

		return Response({'colour_and_images':data},200)


from designer_stylist.api.serializers import DesignerDetailHelperSerializer
class ManufacturerProductDetailAPIView(APIView):
	def get(self,request,*args,**kwargs):
		product_id = self.kwargs['product_id']
		
		obj = Product.objects.select_related('category','subcategory','subsubcategory','user').prefetch_related('available_colours').get(id=product_id, active=True)
		data = ProductDetailSerializer(obj,context={'request':request}).data

		profile = Profile.objects.filter(user=obj.user).first()
		profile_data = DesignerDetailHelperSerializer(profile).data

		best_selling = Product.objects.filter(category=obj.category,subsubcategory=obj.subsubcategory,subcategory=obj.subcategory,active=True,is_deleted=False).select_related('category','subcategory','subsubcategory','user').prefetch_related('available_colours').exclude(id=product_id).order_by('qty_sold')
		best_selling_data = ProductListSerializer(best_selling,many=True).data
		return Response({
			'product_detail':data,
			'profile_data':profile_data,
			'best_selling':best_selling_data
			},
			status=HTTP_200_OK)


class ManufacturerProductDetailByColourAPIView(APIView):
	def get(self,request,*args,**kwargs):
		product_id = self.kwargs['product_id']
		colour_id = self.kwargs['colour_id']

		obj = Product.objects.select_related('category','subcategory','subsubcategory','user').prefetch_related('available_colours').get(id=product_id, active=True)
		data = ProductDetailSerializer(obj,context={'colour_id':colour_id,'request':request}).data

		profile = Profile.objects.filter(user=obj.user).first()
		profile_data = DesignerDetailHelperSerializer(profile).data

		best_selling = Product.objects.filter(category=obj.category,subsubcategory=obj.subsubcategory,subcategory=obj.subcategory,active=True).select_related('category','subcategory','subsubcategory','user').prefetch_related('available_colours').exclude(id=product_id).order_by('qty_sold')
		best_selling_data = ProductListSerializer(best_selling,many=True).data
		return Response({
			'product_detail':data,
			'profile_data':profile_data,
			'best_selling':best_selling_data,
			'mf':True
			},
			status=HTTP_200_OK)


class ProductDetailForWebViewAPIView(APIView):
	def get(self,request,*args,**kwargs):
		product_id = self.kwargs['product_id']
		
		obj = Product.objects.select_related('category','subcategory','subsubcategory').prefetch_related('size','colour').get(id=product_id, active=True)
		data = ProductDetailSerializer(obj,context={'request':request}).data
		return Response(data,status=HTTP_200_OK)
		

class HomePage(APIView):
	def get(self,request):
		cats   = Category.objects.filter(active=True)
		category = CategoryListSeializer(cats,many=True).data
		imgs  = HomePageImage.objects.filter(active=True)
		home_image = HomeImageSerializer(imgs,many=True).data
		products = Product.objects.filter(active=True,is_deleted=False).order_by('-created_date')[:10]
		product = ProductListSerializer(products, many=True).data
		home = {}
		home['category'] = category
		home['home_image'] = home_image
		home['product']= product
		home['message'] = 'success'

		return Response(home,status=HTTP_200_OK)


class WebHomePage(APIView):
	def get(self,request,*args,**kwargs):
		
		stylist_qs = Profile.objects.filter(role=4).values('user')
		top_stylist = Product.objects.filter(active=True, is_deleted=False, user__in = stylist_qs).order_by('-qty_sold')[:10]
		stylist_product = StylistDesignerProductListSerializer(top_stylist, many=True).data		

		designer_qs  = Profile.objects.filter(role=3).values('user')
		top_designer = Product.objects.filter(active=True, is_deleted=False, user__in = designer_qs).order_by('-qty_sold')[:10]
		designer_product = StylistDesignerProductListSerializer(top_designer, many=True).data
		
		manufacturer_qs =  Profile.objects.filter(role=5).values('user')
		top_manufacturer = Product.objects.filter(active=True, is_deleted=False, user__in = manufacturer_qs).order_by('-qty_sold')[:10]
		manufacturer_product = ProductListSerializer(top_manufacturer, many=True).data
		
		return Response({

			'stylist_products':stylist_product,
			'designer_products':designer_product,
			'manufacturer_products':manufacturer_product,

			}, status=HTTP_200_OK)


class WishListAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]


	def get(self,request,*args,**kwargs):
		wishlist_qs = CustomerProductWishList.objects.filter(user=request.user)
		data = CustomerAllwishListSerializer(wishlist_qs, many=True).data
		return Response({
			'message':'success',
			'response':data,
			},
			status=HTTP_200_OK)



	def post(self,request,*args,**kwargs):
		product_id = request.data.get('product')
		colour_id = request.data.get('selected_colour')
		size_id = request.data.get('selected_size')

		if colour_id=='':
			colour_id=None
		if size_id=='':
			size_id=None
		
		qs = CustomerProductWishList.objects.filter(user=request.user, product_id = product_id)
		if qs.exists():
			obj = qs.first()

			obj.selected_colour_id = colour_id
			obj.selected_size = size_id
			obj.save()
			return Response({
			'message':'successfully added in wishlist',

				},status=HTTP_200_OK)

		CustomerProductWishList.objects.create(user=request.user, product_id = product_id, selected_colour_id=colour_id,selected_size=size_id)
		return Response({
			'message':'successfully added in wishlist',

				},status=HTTP_200_OK)

		

class DeleteFromWishlistAPIView(APIView):

	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def delete(self,request,*args,**kwargs):
		product_id = self.kwargs.get('product_id')
		try:
			CustomerProductWishList.objects.get(user=request.user,product_id=product_id).delete()
			return Response({
					'message':'Removed from wishlist',
						},status=HTTP_200_OK)
		except:
			return Response({
					'message':'No product for remove',
						},status=HTTP_400_BAD_REQUEST)




from django.db.models import Sum,F,Q
from django.utils import timezone
import datetime


class CartListAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]


	def post(self,request,*args,**kwargs):
		product_id = request.data.get('product')
		size = request.data.get('selected_size')
		qty = request.data.get('selected_quantity') 
		colour_id = request.data.get('selected_colour')

		if product_id != '' and size != '' and colour_id != '': 

			### first check quantity is available or not
			# try:
			colour_qs = ProductAvailableColourWithSizeQty.objects.filter(id = colour_id)
			if colour_qs.exists():
				colour_obj = colour_qs.first()
				size_obj = colour_obj.size_and_qty.filter(size=size)
				if size_obj.exists():
					if int(qty) > size_obj.first().available_qty:
						return Response({

								'message':'No more stoke available for this size',

								},200)
					else:
						qs = CustomerProductCart.objects.filter(user = request.user, product_id=product_id,selected_size=size,
						selected_colour = colour_id, is_ordered=False, is_product_deleted=False)
						if qs.exists():
							obj = qs.first()
							obj.selected_size = size
							obj.save()
							return Response({

								'message':'successfully added in cart',

									},status=HTTP_200_OK)

						CustomerProductCart.objects.create(user = request.user,  product_id=product_id, selected_colour_id=colour_id, selected_size =size ,selected_quantity=qty)
						return Response({

							'message':'successfully added in cart',

							},status=HTTP_200_OK)

				return Response({

					'message':'Wrong size selection',

					},status=HTTP_400_BAD_REQUEST)		

			
			return Response({

				'message':'Wrong colour id',

				},status=HTTP_400_BAD_REQUEST)

		return Response({

				'message':'Please select colour and size of Product',

					},status=HTTP_400_BAD_REQUEST)



	def get(self,request,*args,**kwargs):

		cart_qs = CustomerProductCart.objects.filter(user=request.user, is_ordered=False, is_product_deleted=False).order_by('-created')
		data = CustomerCartAllProductListSerializer(cart_qs, many=True).data
		price_details = {}


		price = cart_qs.aggregate(price=Sum(F('selected_colour__actual_price')*F('selected_quantity')))['price']
		print(price)
		saved_ammount = cart_qs.aggregate(total = Sum(F('selected_colour__actual_price')*F('selected_quantity') - F('selected_colour__special_price')*F('selected_quantity')))['total']
		if saved_ammount is None:
			saved_ammount = 0
		if price is None:
			price = 0
		# total = zero_offer_product + offered_product

		price_details['items'] = cart_qs.count()
		price_details['price'] = price
		price_details['saved_ammount'] = saved_ammount
		price_details['shipping_charges'] = 0
		price_details['coupon_applied'] = 0
		price_details['grand_total']=price-saved_ammount-0

		today_date = datetime.datetime.now().date()
		print(today_date)
		coupon_qs = CouponCode.objects.filter(Q(valid_from__lte= today_date) & Q(valid_to__gte= today_date),is_active=True).values('id','code','description','terms_and_cond')
		coupons_data = CouponListSerializer(coupon_qs,many=True).data

		return Response({
			'cart_items':data,
			'price_details':price_details,
			'coupons':coupons_data

			},status=HTTP_200_OK)




class DeleteFromCartAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]


	def delete(self,request,*args,**kwargs):
		cart_id = self.kwargs.get('cart_id')
		try:
			CustomerProductCart.objects.get(id=cart_id).delete()
			return Response({
					'message':'Removed from cart',
						},status=HTTP_200_OK)
		except:
			return Response({
					'message':'No product for remove',
						},status=HTTP_400_BAD_REQUEST)



class CouponApplyCheckingAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request,*args,**kwargs):
		coupon = request.data.get('coupon')
		# product_id = request.data.get('product')

		# product = product_id.split(',')

		# print(product)

		if request.data.get('grand_total') is None or request.data.get('grand_total')== '' or request.data.get('product') == '':
			return Response({
						'message':'Please provide grand total and product id',
							},status=HTTP_400_BAD_REQUEST)

		today_date = datetime.datetime.now().date()
		coupon_qs = CouponCode.objects.filter(code = coupon , valid_from__lte = today_date, valid_to__gte = today_date, is_active =True)

		if coupon_qs.exists():

			# case first checking 
			coupon_obj =  coupon_qs.first()
			if coupon_obj.is_for_all_user == True and coupon_obj.is_for_all_product == True:
				coupon_limit_qs = CoupanCodeUseLimit.objects.filter(user=request.user,coupon=coupon_obj)
				
				if coupon_limit_qs.exists():

					# repeated user 

					coupon_limit_obj  = coupon_limit_qs.first()
					if coupon_limit_obj.used  < coupon_obj.usage_limit:

						

						if coupon_obj.coupon_type == '2': # amount
							grand_total = request.data.get('grand_total')
							if int(grand_total) >= int(coupon_obj.value):
								coupon_discount = coupon_obj.value
								new_grand_total = int(grand_total) - int(coupon_discount)
							else:
								coupon_discount = grand_total
								new_grand_total = 0


							return Response({
									'message':'coupon applied successfully',
									'grand_total':new_grand_total,
									'coupon_applied':coupon_discount,
									},status=HTTP_200_OK)


						if coupon_obj.coupon_type == '1':
							grand_total = request.data.get('grand_total')
							coupon_discount = (int(grand_total)*int(coupon_obj.value))//100

							print(coupon_discount)

							if coupon_discount > int(coupon_obj.max_amount):
								coupon_discount  = coupon_obj.max_amount
								new_grand_total = int(grand_total) - int(coupon_discount)
							else:
								new_grand_total = int(grand_total) - coupon_discount


							return Response({
									'message':'coupon applied successfully',
									'grand_total':new_grand_total,
									'coupon_applied':coupon_discount,
									},status=HTTP_200_OK)

					return Response({
						'message':'You have exceeded maximum use limit of this coupon',
							},status=HTTP_400_BAD_REQUEST)



				# first time users

				else:


					if coupon_obj.coupon_type == '2': # amount
						grand_total = request.data.get('grand_total')
						if int(grand_total) >= int(coupon_obj.value):
							coupon_discount = coupon_obj.value
							new_grand_total = int(grand_total) - int(coupon_discount)
						else:
							coupon_discount = grand_total
							new_grand_total = 0


						return Response({
								'message':'coupon applied successfully',
								'grand_total':new_grand_total,
								'coupon_applied':coupon_discount,
								},status=HTTP_200_OK)


					if coupon_obj.coupon_type == '1':
						grand_total = request.data.get('grand_total')
						coupon_discount = (int(grand_total)*int(coupon_obj.value))//100

						print(coupon_discount)

						if coupon_discount > int(coupon_obj.max_amount):
							coupon_discount  = coupon_obj.max_amount
							new_grand_total = int(grand_total) - int(coupon_discount)
						else:
							new_grand_total = int(grand_total) - coupon_discount


						return Response({
								'message':'coupon applied successfully',
								'grand_total':new_grand_total,
								'coupon_applied':coupon_discount,
								},status=HTTP_200_OK)

			else:
				product = CustomerProductCart.objects.filter(user=request.user, is_ordered=False, is_product_deleted=False).values_list('product',flat=True)
				print(product)

				if coupon_obj.is_for_all_product ==False and coupon_obj.is_for_all_user==False:
					coupon_qs = coupon_qs.filter(selected_product__in =product,  selected_users=request.user)

				if coupon_obj.is_for_all_product ==True and coupon_obj.is_for_all_user==False:
					coupon_qs = coupon_qs.filter(selected_users=request.user)

				if coupon_obj.is_for_all_product == False and coupon_obj.is_for_all_user==True: 
					coupon_qs = coupon_qs.filter(selected_product__in =product)
					
				if coupon_qs.exists():

					if coupon_obj.coupon_type == '2': # amount
						grand_total = request.data.get('grand_total')
						if int(grand_total) >= int(coupon_obj.value):
							coupon_discount = coupon_obj.value
							new_grand_total = int(grand_total) - int(coupon_discount)
						else:
							coupon_discount = grand_total
							new_grand_total = 0


						return Response({
								'message':'coupon applied successfully',
								'grand_total':new_grand_total,
								'coupon_applied':coupon_discount,
								},status=HTTP_200_OK)


					if coupon_obj.coupon_type == '1':
						grand_total = request.data.get('grand_total')
						coupon_discount = (int(grand_total)*int(coupon_obj.value))//100

						print(coupon_discount)

						if coupon_discount > int(coupon_obj.max_amount):
							coupon_discount  = coupon_obj.max_amount
							new_grand_total = int(grand_total) - int(coupon_discount)
						else:
							new_grand_total = int(grand_total) - coupon_discount


						return Response({
								'message':'coupon applied successfully',
								'grand_total':new_grand_total,
								'coupon_applied':coupon_discount,
								},status=HTTP_200_OK)

				return Response({
							'message':'You are not eligible for this coupon code',
								},status=HTTP_400_BAD_REQUEST)	
		return Response({
							'message':'Invalid Coupon or coupon may be expired',
								},status=HTTP_400_BAD_REQUEST)



class RemoveCouponAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request,*args,**kwargs):
		data = request.data

		if data.get('grand_total') is not None and data.get('grand_total') !='' and  data.get('coupon_applied') !='' and data.get('coupon_applied') is not None:
			return Response({
						'message':'coupon removed successfully',
						'grand_total':int(data.get('grand_total'))+int(data.get('coupon_applied')),
						'coupon_applied':0
						},status=HTTP_200_OK)

		return Response({
				'message':'please give grand_total and coupon_applied both',
					},status=HTTP_400_BAD_REQUEST)



class ChangeCartItems(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request,*args,**kwargs):
		data = request.data
		try:

		
			obj = CustomerProductCart.objects.select_related('product').get(pk=data.get('cart_id'))
			
		except:
			return Response({
				'message':'invalid cart_id',
					},status=HTTP_400_BAD_REQUEST)


		colour_qs = ProductAvailableColourWithSizeQty.objects.filter(id = obj.selected_colour.id)
		if colour_qs.exists():
			colour_obj = colour_qs.first()
			size_obj = colour_obj.size_and_qty.filter(size=obj.selected_size)
			if size_obj.exists():
				if int(data.get('quantity')) > size_obj.first().available_qty:
					return Response({

							'message':'No more stock available for this size',

							},400)
				else:
					obj.selected_quantity = data.get('quantity')
					obj.save()

					### we can eliminate by inheritance

					cart_qs = CustomerProductCart.objects.filter(user=request.user, is_ordered=False, is_product_deleted=False)
					price_details = {}


					price = cart_qs.aggregate(price=Sum(F('selected_colour__actual_price')*F('selected_quantity')))['price']
					saved_ammount = cart_qs.aggregate(total = Sum(F('selected_colour__actual_price')*F('selected_quantity') - F('selected_colour__special_price')*F('selected_quantity')))['total']
					if saved_ammount is None:
						saved_ammount = 0
					if price is None:
						price = 0

					coupon_applied = data.get('coupon_applied')
					if coupon_applied== None or coupon_applied=='':
						coupon_applied = 0
					else:
						coupon_applied = coupon_applied
					price_details['items'] = cart_qs.count()
					price_details['price'] = price
					price_details['saved_ammount'] = saved_ammount
					price_details['shipping_charges'] = 0
					price_details['coupon_applied'] = coupon_applied

					price_details['grand_total']=price-saved_ammount-0-int(coupon_applied)


					return Response({
									'message':'successfully changed product quantity',
									'price_details':price_details
										},status=HTTP_200_OK)

			return Response({

					'message':'Wrong size selection',

					},status=HTTP_400_BAD_REQUEST)		
		return Response({

				'message':'Wrong colour id',

				},status=HTTP_400_BAD_REQUEST)

	

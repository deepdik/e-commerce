from rest_framework.generics import (
		ListAPIView,
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
from designer_stylist.models import * 
from product.models import Product,CustomerProductWishList,CustomerProductCart,ProductAvailableColourWithSizeQty,ProductImage,Colour,ProductImageByColour,CouponCode,DeliveryDistanceManagement
from .serializers import *
from rest_framework.authentication import SessionAuthentication
from orders.models import CustomerOrders
from accounts.models import UserOtherInfo
from rest_framework.permissions import IsAuthenticated
from admin_panel.models import Faq
from django.db.models import Sum
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication
from accounts.api.permissions import *
# is owner authentication 


class DeleteAppInAchievementImgAPIView(APIView):

	 def post(self,request,*args,**kwargs):

	 	image_id = self.kwargs['image_id']
	 	
	 	try:

	 		Image.objects.get(pk=image_id).delete()
	 	except:
	 		return Response({
				
			 	'message':'No image for delete'
				},status=HTTP_404_NOT_FOUND)

	 	return Response({
				
				'message':'deleted successfully'
				},status=HTTP_200_OK)


# allow only for owner

class StylistDesignerSectionDeleteAPIView(APIView):

	def post(self,request,*args,**kwargs):
	
		try:
			StylistDesignerSection.objects.get(id=self.kwargs.get('section_id')).delete()
		except:
			return Response({
				
			 	'message':'No Section for delete'
				},status=HTTP_404_NOT_FOUND)

		return Response({
				
				'message':'deleted successfully'
				},status=HTTP_200_OK)
	

# allow only for owner

class StylistDesignerProductRemoveAPIView(APIView):

	def post(self,request,*args,**kwargs):
		data =request.data
		print(data['section_id'])	
		try:
			obj = Product.objects.get(id=self.kwargs.get('product_id'))
			obj.usersection.remove(*data['section_id'])
			obj.save()
		except:	
			return Response({
					
				 	'message':'No Product for Remove'
					},status=HTTP_404_NOT_FOUND)

		return Response({
				
				'message':'Removed successfully'
				},status=HTTP_200_OK)
		


# allow only for owner

class StylistDesignerProductAddAPIView(APIView):

	def post(self,request,*args,**kwargs):
		data =request.data
		print(request.data['product'])
		
		try:
			qs = Product.objects.filter(id__in = data['product'])
			for obj in qs:
				obj.usersection.add(self.kwargs.get('section_id'))
		except:
		
			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'added successfully'
				},status=HTTP_200_OK)

		

# allow only for owner

class StylistDesignerProductDeleteAPIView(APIView):
	permission_classes = (IsAuthenticated,IsStaffUser)
	authentication_classes = [SessionAuthentication]
	def post(self,request,*args,**kwargs):	
		print(request.user)	
		product_id  = self.kwargs.get('product_id')
		try:

			# if product is connected to order table then dont delete it
			prod_obj = Product.objects.get(id = product_id)
			qs = CustomerOrders.objects.filter(cart__product__id = product_id)
			if not qs.exists():
				# prod_obj.delete()
				CustomerProductCart.objects.filter(product=prod_obj).delete()
			else:
				prod_obj.is_deleted = True
				prod_obj.active = False
				prod_obj.save()
				CustomerProductCart.objects.filter(product=prod_obj).update(is_product_deleted=True)
				CustomerProductWishList.objects.filter(product=prod_obj).delete()
		except:
			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=500)

		return Response({
				
				'message':'Deleted Successfully'
				},status=200)
		



class StylistDesignerProductVarientDeleteAPIView(APIView):

	def post(self,request,*args,**kwargs):		
		
		try:	
			prod_col_obj = ProductAvailableColourWithSizeQty.objects.get(id = self.kwargs.get('varient_id'))
			qty = prod_col_obj.size_and_qty.all().aggregate(Sum('available_qty'))
			
			if CustomerProductCart.objects.filter(selected_colour=prod_col_obj).exists():
				prod_col_obj.is_active=False
				prod_col_obj.save()
			else:
				prod_col_obj.delete()
			prod_obj = Product.objects.get(id = self.kwargs.get('product_id'))
			
			prod_available_colour  =  prod_obj.available_colours.filter(is_active=True)
			
			if prod_available_colour.exists():
				min_price_obj = prod_available_colour.order_by('special_price')[0]
				prod_obj.min_price = min_price_obj.special_price
				prod_obj.offer_of_min = min_price_obj.offer
				prod_obj.total_quantity = abs(prod_obj.total_quantity - qty['available_qty__sum'])
				prod_obj.save()
			else:
				prod_obj.min_price = 0
				prod_obj.offer_of_min = 0
				prod_obj.is_row = True
				prod_obj.active = False
				prod_obj.total_quantity = 0
				prod_obj.save()
		except:
			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Deleted Successfully'
				},status=HTTP_200_OK)
		


# all is owner 

class StylistDesignerCategoryAPIView(APIView):

	def post(self,request,*args,**kwargs):		
		
		try:
			StylistDesignerCategory.objects.get(id = self.kwargs.get('category_id')).delete()
		except:
		
			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Deleted Successfully'
				},status=HTTP_200_OK)

	def put(self,request,*args,**kwargs):		
		
		try:
			obj  =StylistDesignerCategory.objects.get(id = self.kwargs.get('category_id'))
			obj.name = request.data.get('name')
			obj.save()
		except:
		
			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Updated Successfully'
				},status=HTTP_200_OK)



# all only for is owner

class StylistDesignerProductActiveInactiveAPIView(APIView):
	def post(self,request,*args,**kwargs):

		print(self.kwargs.get('status'),self.kwargs.get('product_id'))
		try:
			obj = Product.objects.get(id = self.kwargs.get('product_id'))
			if obj.is_row ==True:
				return Response({				
					'message':'Please add some variants with this product to make it active'
					},status=HTTP_200_OK)
			else:
				obj.active = self.kwargs.get('status')
				obj.save()
		except:
			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Status Change Successfully'
				},status=HTTP_200_OK)


class StylistDesignerProductImageDeleteAPIView(APIView):
	def post(self,request,*args,**kwargs):

		try:			
			ProductImage.objects.get(id =self.kwargs.get('image_id')).delete()
		except:

			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Image Deleted Successfully'
				},status=HTTP_200_OK)



class StylistDesignerProductColourImageDeleteAPIView(APIView):
	def post(self,request,*args,**kwargs):

		try:			
			ProductImageByColour.objects.get(id =self.kwargs.get('image_id')).delete()
		except:

			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Image Deleted Successfully'
				},status=HTTP_200_OK)




class StylistDesignerProductColourDeleteAPIView(APIView):
	def post(self,request,*args,**kwargs):

		try:			
			Colour.objects.get(id =self.kwargs.get('colour_id')).delete()
		except:

			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Colour Deleted Successfully'
				},status=HTTP_200_OK)


# all only for is admin

class CouponAPIView(APIView):

	def get(self,request,*args,**kwargs):
		try:			
			obj = CouponCode.objects.get(id =self.kwargs.get('coupon_id'))
			data= CouponSerializer(obj).data
			return Response({

				'coupon_data':data

				},status=HTTP_200_OK)

		except:

			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)


	def delete(self,request,*args,**kwargs):
		try:			
			CouponCode.objects.get(id =self.kwargs.get('coupon_id')).delete()
		except:

			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Coupon deleted successfully'
				},status=HTTP_200_OK)


class CouponStatusChangeAPIView(APIView):


	def post(self,request,*args,**kwargs):
		try:			
			obj = CouponCode.objects.get(id =self.kwargs.get('coupon_id'))
			obj.is_active = self.kwargs.get('status')
			obj.save()
		except:

			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Coupon status changed successfully'
				},status=HTTP_200_OK)




class DeliveryChagresDeleteAPIView(APIView):
	def delete(self,request,*args,**kwargs):

		try:			
			DeliveryDistanceManagement.objects.get(id =self.kwargs.get('deliveryCharge_id')).delete()
		except:

			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Deleted Successfully'
				},status=HTTP_200_OK)



class FAQDeleteAPIView(APIView):
	def delete(self,request,*args,**kwargs):

		try:			
			Faq.objects.get(id =self.kwargs.get('faq_id')).delete()
		except:

			return Response({
					
				 	'message':'Somthing went wrong. Please try after some time'
					},status=HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({
				
				'message':'Deleted Successfully'
				},status=HTTP_200_OK)
	
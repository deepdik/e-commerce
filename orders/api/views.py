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
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_jwt.authentication import  JSONWebTokenAuthentication

from .serializers import *
from orders.models import *

import logging
logger = logging.getLogger('payments')

from product.models import CustomerProductCart
class DeliveryAddressAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		user= request.user 
		qs = CustomerAddress.objects.filter(user=request.user, is_active=True)
		data  = DeliveryAddressViewSerializer(qs,many=True).data

		return Response({
			'delivery_addresses':data,
			'message':'success'

			}, status=HTTP_200_OK)

	def post(self,request,*args,**kwargs):
		data = request.data

		serializer = DeliveryAddressAddSerializer(data=data)

		if serializer.is_valid():
			serializer.validated_data['user']=request.user
			serializer.save()
			return Response({
				'message':'address added successfully'
				} ,200)

		return Response(serializer.errors ,400)


class ActionOnDeliveryAddressAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		addr_id = self.kwargs.get('addr_id')
		try:
			
			obj = CustomerAddress.objects.get(pk = addr_id, user=request.user, is_active=True)
		except:
			return Response({
					
					'message':'Invalid address id'

					}, status=HTTP_400_BAD_REQUEST)

		data  = DeliveryAddressViewSerializer(obj).data

		return Response({
					'delivery_address':data,
					'message':'success'

					}, status=HTTP_200_OK)


	def delete(self,request,*args,**kwargs):
		addr_id = self.kwargs.get('addr_id')
		try:
			# checking, is address with any order

			qs = CustomerOrders.objects.filter(address = addr_id)
			if qs.exists():
				obj = CustomerAddress.objects.get(pk = addr_id,user=request.user)
				obj.is_active=False
				obj.save()
			else:

				CustomerAddress.objects.get(pk = addr_id,user=request.user).delete()
		except:
			return Response({
					
					'message':'Invalid address id'

					}, status=HTTP_400_BAD_REQUEST)

		return Response({
					
					'message':'Address deleted successfully '

					}, status=HTTP_200_OK)

	def put(self,request,*args,**kwargs):
		addr_id = self.kwargs.get('addr_id')
		data = request.data
		try:
			obj = CustomerAddress.objects.get(pk = addr_id,user=request.user,is_active=True)
		except:
			return Response({
				'message':'No address found'
				},400)
		serializer = DeliveryAddressAddSerializer(data=data, instance = obj )

		if serializer.is_valid():
			serializer.validated_data['user']=request.user
			serializer.save()
			return Response({
				'message':'address updated successfully'
				} ,200)

		return Response(serializer.errors ,400)


from django.db.models import Sum

def make_order(self,request,*args,**kwargs):

	user = request.user
	data = request.data
	all_cart_item = dict(request.data).get('cart')

	serializer = MakeOrderAPIViewSerializer(data=data)
	if serializer.is_valid():
		serializer.validated_data['user']=request.user
		obj = serializer.save()
		
		cart_list = [ OrderedProductStatus(user=request.user,order_id = obj.id ,cart_id = cart_id) for cart_id in all_cart_item]     
		OrderedProductStatus.objects.bulk_create(cart_list)

		### remove from cart 

		cart_qs = CustomerProductCart.objects.filter(id__in = all_cart_item)
		cart_qs.update(is_ordered=True)
		
		# decrease product available stock quantity

		for cart_obj in cart_qs:
			size_qs 	= cart_obj.selected_colour.size_and_qty.filter(size = cart_obj.selected_size)
			size_obj 	= size_qs.first()
			size_obj.available_qty = size_obj.available_qty - cart_obj.selected_quantity
			product_obj = cart_obj.product
			if cart_obj.selected_colour.size_and_qty.aggregate(Sum('available_qty'))['available_qty__sum'] == 0 :
				colour_obj = cart_obj.selected_colour
				colour_obj.is_out_of_stock = True
				colour_obj.save()

				# min_price_obj = product_obj.available_colours.filter(is_active=True, is_out_of_stock=False).order_by('special_price')
				# if min_price_obj.exists():
				# 	product_obj.min_price = min_price_obj.special_price
				# 	product_obj.offer_of_min = min_price_obj.offer

			size_obj.save()

			if product_obj.total_quantity - cart_obj.selected_quantity == 0:
				product_obj.stock_status = False
				# product_obj.active = False
			product_obj.total_quantity = abs(product_obj.total_quantity - cart_obj.selected_quantity)
			product_obj.qty_sold = product_obj.qty_sold + cart_obj.selected_quantity
			product_obj.save()

		return {
				'message':'Order placed successfully',
				'order_id':obj.id,
				'status':200
				}

	return {
				'message':serializer.errors,
				'status':400
				}


class MakeOrderAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request,*args,**kwargs):
	
		user = request.user
		data = request.data
		print(data)

		serializer = MakeOrderAPIViewSerializer(data=data)
		if serializer.is_valid():
			serializer.validated_data['user']=request.user
			obj = serializer.save()

			## create individual product status

			cart_list = [ OrderedProductStatus(user=request.user,order_id = obj.id ,cart_id = cart_id) for cart_id in request.data.get('cart')]     
			OrderedProductStatus.objects.bulk_create(cart_list)

			### remove from cart 

			cart_qs = CustomerProductCart.objects.filter(id__in = request.data.get('cart')).update(is_ordered=True)



			return Response({
					'message':'Order placed successfully'
					} ,200)

		return Response(serializer.errors ,400)


from product.api.serializers import CustomerCartAllProductListSerializer
from product.models import CustomerProductCart

class AllOrderProductHistoryAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]


	def get(self,request,*args,**kwargs):
		history = OrderedProductStatus.objects.filter(user=request.user, order_status__in=[4,5]).order_by('-created')
		print(history,'history')
		history_data = AllOrderProductHistorySerializer(history,many=True).data
		ongoing = OrderedProductStatus.objects.filter(user=request.user, order_status__in=[1,2,3]).order_by('-created')
		print(ongoing,'ongoing')
		ongoing_data = AllOrderProductHistorySerializer(ongoing,many=True).data
		return Response({
				'history':history_data,
				'ongoing':ongoing_data,

				'message':'success'
				} ,200)

class OrderedProductHistoryAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		try:
			order_detail = OrderedProductStatus.objects.get(id = self.kwargs.get('id'), user = request.user )
		except:
			return Response({
					'message':'Invalid id'
					} ,400)

		order_detail_data = OrderdProductHistorySerializer(order_detail,context={'request':request}).data

		return Response({
				'order_detail':order_detail_data,

				'message':'success'
				} ,200)


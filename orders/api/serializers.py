

from rest_framework.serializers import(
     ModelSerializer,
     EmailField, 
     CharField,
     ValidationError,
     SerializerMethodField,
     Serializer,
     ImageField,
     IntegerField
     )

from orders.models import *
from rest_framework.exceptions import APIException
class APIException400(APIException):
    status_code = 400


class DeliveryAddressViewSerializer(ModelSerializer):
	class Meta:
		model = CustomerAddress
		fields  = '__all__'


class DeliveryAddressAddSerializer(ModelSerializer):
	class Meta:
		model = CustomerAddress
		fields  = [
			'name',
			'country_code',
			'phonenum',
			'city',
			'pincode',
			'state',
			'area_street',
			'flat_building',
			'addr_type',
			'landmark',
			'lat',
			'log',
		]

	def validate(self,data):
		print(len(data['phonenum']))
		if not data['phonenum'].isdigit() or  not len(data['phonenum']) < 13:
			raise APIException400({
                'message':'Please correct your number',
                
                })
		if not data['pincode'].isdigit() or not len(data['pincode']) < 8:
			raise APIException400({
                'message':'Please correct your pin code',
                })
		return data


class MakeOrderAPIViewSerializer(ModelSerializer):
	coupon_code  =  CharField(allow_blank=True)


	class Meta:
		model = CustomerOrders
		fields  = [
			'cart',
			'address',
			'payment',
			'is_coupon_applied',
			'item',
			'coupon_code',
			'coupon_off',
			'price',
			'saved_amount',
			'shipping_charges',
			'grand_total'
			]

class ProductOrderedDetailSerializer(ModelSerializer):
	address = SerializerMethodField()



	def get_address(self,instance):
		data = DeliveryAddressAddSerializer(instance.address).data
		return data

	class Meta:
		model = CustomerOrders
		fields  = [
			'address',
			'payment',
			'is_coupon_applied',
			]



from product.api.serializers import CustomerCartAllProductListSerializer

class AllOrderProductHistorySerializer(ModelSerializer):
	product_detail = SerializerMethodField()
	order_id =SerializerMethodField()

	def get_product_detail(self,instance):
		data = CustomerCartAllProductListSerializer(instance.cart).data
		return data

	def get_order_id(self,instance):
		return instance.order.id

	class Meta:
		model = OrderedProductStatus
		fields = [
			'id',
			'created',
			'order_status',
			'order_id',
			'product_detail',

		]

class OrderedProductReviewsSerializer(ModelSerializer):
	class Meta:
		model = OrderedProductReviews
		fields = '__all__'



class OrderdProductHistorySerializer(ModelSerializer):
	product_detail = SerializerMethodField()
	order_detail = SerializerMethodField()
	# reviews  =SerializerMethodField()
	order_status = SerializerMethodField()

	def get_product_detail(self,instance):
		data = CustomerCartAllProductListSerializer(instance.cart).data
		return data

	def get_order_status(self, instance):
		return int(instance.order_status)

	def get_order_detail(self,instance):
		data = ProductOrderedDetailSerializer(instance.order).data
		return data


	# def get_reviews(self,instance):
	# 	qs = OrderedProductReviews.objects.filter(user = self.context['request'].user, order=instance.id)
	# 	if qs.exists():

	# 		data = OrderedProductReviewsSerializer(qs.first()).data
	# 		return data
	# 	return []
	class Meta:
		model = OrderedProductStatus
		fields = [
			'id',
			'created',
			'order_status',
			'order_detail',
			'product_detail',
			# 'reviews',

		]
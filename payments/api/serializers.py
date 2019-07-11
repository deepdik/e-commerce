from rest_framework.serializers import(
	 ModelSerializer,
	 SerializerMethodField,
	 Serializer,
	 CharField,

	 
	 )

from payments.models import *
from rest_framework.exceptions import APIException

class APIException400(APIException):
	status_code = 400


class PaymentSerializer(Serializer):
	source_token 	= CharField(required=True)
	grand_total 	= CharField(required=True)
	currency 		= CharField(required=True)



class ListOfSavedCardSerializer(ModelSerializer):
	class Meta:
		model 	= StripeCustomer 
		fields 	= ['card','source_token','name']
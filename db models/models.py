from django.db import models
from django.contrib.auth.models import User

PAYMENT_METHOD = (('1', 'Card'),('2', 'Net banking'),('3' ,'Cash on delivery'))
PAYMENT_STATUS = (('1','Successed'),('2','Failed'))

from orders.models import CustomerOrders

class StripeCustomer(models.Model):
	user 		   = models.ForeignKey(User, null=True ,on_delete=models.SET_NULL)
	stripe_cus_id  = models.CharField(max_length=300,blank=True,null=True)
	source_token   = models.CharField(max_length =300,blank=True,null=True)
	card           = models.CharField(max_length=40,blank=True,null=True)
	name           = models.CharField(max_length = 40,blank=True,null=True)
	created        = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.first_name + str(self.id)


class PaymentHistory(models.Model):
	user 		   		= models.ForeignKey(User, null=True ,on_delete=models.SET_NULL)
	description    		= models.CharField(max_length=200)
	payment_type   		= models.CharField(max_length=30,choices=PAYMENT_METHOD)
	status_message 		= models.TextField(blank=True,null=True)
	payment_id     		= models.CharField(max_length=200,blank=True,null=True)
	amount      		= models.CharField(max_length=100,blank=True,null=True)
	captured            = models.BooleanField(default=False)
	order_id            = models.ForeignKey(CustomerOrders,null=True,on_delete=models.SET_NULL)
	payment_detail      = models.CharField(max_length =100, blank=True,null=True)
	def __str__(self):
		return self.user.first_name + str(self.id)

from django.db import models
from django.contrib.auth.models import User
from product.models import Product,CustomerProductCart,CouponCode
from django.core.validators import MaxValueValidator, MinValueValidator




ADDTYPE = (('1', 'Work'),('2', 'Home'),('3' ,'Other'))
PAYMENT_METHOD = (('1', 'Card'),('2', 'Net banking'),('3' ,'Cash on delivery'))

ORDER_STATUS  = (('1', 'Ordered'),('2', 'Packed'),('3' ,'Shipped'),('4' ,'Delivered'),('5' ,'Canceled'))

class CustomerAddress(models.Model):
	user 	 		= models.ForeignKey(User, on_delete=models.CASCADE)
	name   			= models.CharField(max_length=40)
	country_code    = models.CharField(max_length=10)
	phonenum 		= models.CharField(max_length=15)
	city     		= models.CharField(max_length=40)
	pincode      	= models.CharField(max_length=10)
	state    		= models.CharField(max_length=30)
	area_street 	= models.CharField(max_length=100,blank=True,null=True)
	flat_building 	= models.CharField(max_length=100,blank=True,null=True)
	addr_type       = models.CharField(max_length=10,choices=ADDTYPE)
	landmark 		= models.CharField(max_length=100,blank=True,null=True)
	
	# in case of pin point address

	lat             = models.CharField(max_length=30,blank=True,null=True)
	log             = models.CharField(max_length=30,blank=True,null=True)


	# not delete address when already attached with any order

	is_active      = models.BooleanField(default=True)


	def __str__(self):
		return self.user.first_name + '-'+ str(self.id)



class CustomerOrders(models.Model):
	'''
	ongoing and history all other stuffs
	'''


	user  				= models.ForeignKey(User, on_delete=models.CASCADE)
	cart 				= models.ManyToManyField(CustomerProductCart)
	address     		= models.ForeignKey(CustomerAddress, null=True , on_delete=models.SET_NULL)
	payment     		= models.CharField(max_length=50,choices=PAYMENT_METHOD)

	# price detail 

	is_coupon_applied   = models.BooleanField(default=False)
	coupon_code         = models.CharField(blank=True,null=True ,max_length=30 )

	item                = models.CharField(max_length=5,blank=True, null=True)
	price               = models.CharField(max_length=10,blank=True, null=True)
	saved_amount        = models.CharField(max_length=10,blank=True, null=True)
	shipping_charges    = models.CharField(max_length=10,blank=True, null=True)
	coupon_off      	= models.CharField(max_length=10, blank=True, null=True)
	grand_total         = models.CharField(max_length=10,blank=True, null=True)
	created     		= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.first_name + '-'+ str(self.id)

	
class OrderedProductStatus(models.Model):
	user  				= models.ForeignKey(User, on_delete=models.CASCADE)
	order   			= models.ForeignKey( CustomerOrders, null=True , on_delete=models.SET_NULL )
	cart 				= models.ForeignKey( CustomerProductCart, null=True , on_delete=models.SET_NULL )
	order_status        = models.CharField(max_length = 2,default= 1, choices=ORDER_STATUS)
	created     		= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.first_name + '-'+ str(self.id)



class OrderedProductReviews(models.Model):
	'''
	feedback of user after delivery of product
	after rating avg_rating should be change
	'''
	order             	= models.ForeignKey(OrderedProductStatus, on_delete=models.CASCADE)
	user                = models.ForeignKey(User, on_delete=models.CASCADE)
	rating              = models.PositiveIntegerField( validators=[MaxValueValidator(5), MinValueValidator(1)])
	content             = models.TextField(blank=True,null=True)
	created             = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.order) +' - '+str(self.user)+' - '+str(self.rating)








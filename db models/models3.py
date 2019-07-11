from django.db import models
from django.contrib.auth.models import User
from designer_stylist.models import StylistDesignerCategory,StylistDesignerSection
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
# from designer.models import Profile

class Category(models.Model):
	cat_name   		= models.CharField(max_length=50)
	cat_image  		= models.ImageField(upload_to='CatImg')
	banner_image    = models.ImageField(upload_to='CatBannerImg', blank=True,null=True)
	active          = models.BooleanField(default=False)
	des             = models.TextField(blank=True,null=True)

	def __str__(self):
		return self.cat_name

class SubCategory(models.Model):
	category    	= models.ForeignKey(Category, on_delete=models.CASCADE)
	subcat_name   	= models.CharField(max_length=50)
	subcat_image  	= models.ImageField(upload_to='SubCatImg')
	banner_image    = models.ImageField(upload_to='SubCatBannerImg',blank=True,null=True)
	active          = models.BooleanField(default=False)
	des             = models.TextField(blank=True,null=True)
	def __str__(self):
		return self.subcat_name + '-' +self.category.cat_name

class SubSubCategory(models.Model):
	category    		= models.ForeignKey(Category, on_delete=models.CASCADE)
	subcategory    		= models.ForeignKey(SubCategory, on_delete=models.CASCADE)
	subsubcat_name   	= models.CharField(max_length=50)
	subsubcat_image  	= models.ImageField(upload_to='SubSubCatImg')
	banner_image    	= models.ImageField(upload_to='SubSubCatBannerImg',blank=True,null=True)
	active          	= models.BooleanField(default=False)
	des             	= models.TextField(blank=True,null=True)
	def __str__(self):
		return self.subsubcat_name + '-'+self.subcategory.subcat_name+'-'+self.category.cat_name



class ProductFilterTag(models.Model):
	subsubcategory 	= models.ForeignKey(SubSubCategory, on_delete=models.CASCADE)
	tag     		= models.CharField(max_length=30)
	
	def __str__(self):
		return self.subsubcategory.subsubcat_name + '-'+self.tag

class ProductFilterSubTag(models.Model):
	productfiltertag 	= models.ForeignKey(ProductFilterTag,on_delete=models.CASCADE)
	subtag              = models.CharField(max_length=50)

	def __str__(self):
		return self.productfiltertag.tag + '-'+self.subtag

class HomePageImage(models.Model):
	active   =   models.BooleanField(default=False)
	image    =   models.ImageField(upload_to='homepage')



class Size(models.Model):
	id 		= models.IntegerField(primary_key=True)
	size 	=  models.CharField(max_length=10)

	def __str__(self):
		return self.size	


class Colour(models.Model):
	id 			= models.AutoField(primary_key=True)
	colour_code =  models.CharField(max_length=30)
	name 		= models.CharField(max_length=30, blank=True,null=True)	


	# def __str__(self):
	# 	return self.name



class ProductSizeWithQty(models.Model):
	size  			= models.CharField(max_length=10)
	initial_qty 	= models.PositiveIntegerField(blank=True,null=True)
	available_qty 	= models.PositiveIntegerField(blank=True,null=True) 
	stock_status    = models.BooleanField(default=True) # in stock(true)/out of stock(false)
      

	def __int__(self):
	 	return self.id


class ProductAvailableColourWithSizeQty(models.Model):
	colour                  = models.ForeignKey(Colour,null=True,on_delete=models.SET_NULL)
	actual_price            = models.PositiveIntegerField(blank=True,null=True)
	special_price           = models.PositiveIntegerField(blank=True,null=True)
	offer                   = models.CharField(max_length =5 ,blank=True,null=True)
	size_and_qty            = models.ManyToManyField(ProductSizeWithQty,blank=True)
	is_active               = models.BooleanField(default=True)
	def __str__(self):
	 	return self.colour.name +'-'+ str(self.id)


class ProductImageByColour(models.Model):
	'''
	this is for  images of product by colour
	'''
	product_colour_id 	= models.ForeignKey(ProductAvailableColourWithSizeQty, on_delete=models.CASCADE)
	image 				= models.ImageField(upload_to='Product/OtherImg')

	def __int__(self):
		return self.product_colour_id
	

class Product(models.Model):
	category    			= models.ForeignKey(Category, null=True,on_delete=models.SET_NULL)
	subcategory    			= models.ForeignKey(SubCategory,null=True, on_delete=models.SET_NULL)
	subsubcategory    		= models.ForeignKey(SubSubCategory, null=True, on_delete=models.SET_NULL)
	user                	= models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
	usercategory            = models.ForeignKey(StylistDesignerCategory, blank=True ,null=True, on_delete=models.SET_NULL)
	usersection           	= models.ManyToManyField(StylistDesignerSection,blank=True)

	name 					= models.CharField(max_length=150)
	product_filter_tag      = models.ManyToManyField(ProductFilterTag)

	#quantity management

	total_quantity          = models.PositiveIntegerField(blank=True,null=True)

	description             = models.TextField()
	avg_rating              = models.FloatField(default=0.0)

	#will be fill in all case

	# actual_price            = models.PositiveIntegerField(blank=True,null=True)
	
	#applicable only when one product 

	# special_price           = models.PositiveIntegerField(blank=True,null=True)
	# special_date_from       = models.DateTimeField(blank=True,null=True)
	# special_date_to         = models.DateTimeField(blank=True,null=True)
	

	more_info               = models.TextField()
	isfree_delivery         = models.BooleanField(default=False)
	# stock_status            = models.BooleanField(default=True) # in stock(true)/out of stock(false)
	active                  = models.BooleanField(default=False) # active for customers
	main_img                = models.ImageField(upload_to='Product/MainImg',blank=True ,default='Product/default')
	
	#for specifications

	material                = models.CharField(max_length=200,blank=True,null=True) # 
	fit                     = models.CharField(max_length=100,blank=True,null=True) #
	pattern                 = models.CharField(max_length=200,blank=True,null=True) #
	fabric                  = models.CharField(max_length=200,blank=True,null=True)	#
	brand                   = models.CharField(max_length=100,blank=True,null=True) #
	available_colours       = models.ManyToManyField(ProductAvailableColourWithSizeQty,blank=True)
	#filter


	#size                  = models.ManyToManyField(ProductAvailableSizeWithQty ,blank=True)
	# colour               = models.ForeignKey(Colour,null=True ,on_delete=models.SET_NULL)
	
	# THIS IS FOR SUBPRODUCTS
	# available_subproducts   = models.ManyToManyField("self",blank=True)
	
	#for filter
	created_date            = models.DateTimeField(auto_now_add=True)
	qty_sold                = models.PositiveIntegerField(blank=True,null=True)
	min_price               = models.PositiveIntegerField(default=0,blank=True,null=True)
	# offer of min price
	offer_of_min            = models.PositiveIntegerField(blank=True,default=0,null=True)

	is_row                  = models.BooleanField(default=True)

	def __str__(self):
		return self.name+'-'+ str(self.id)


class ProductAvailableAllColour(models.Model):
	product 				= models.ForeignKey(Product,null=True, on_delete=models.CASCADE)
	colour      			= models.ForeignKey(Colour,null=True ,on_delete=models.SET_NULL)
	in_stock                = models.BooleanField(default=True)


	def __str__(self):
		return self.product.name

class ProductAvailableSize(models.Model):
	product 				= models.ForeignKey(Product, on_delete=models.CASCADE)
	size          			= models.CharField(max_length=60)

	def __str__(self):
		return self.product.name

class ProductAvailableColour(models.Model):
	product 				= models.ForeignKey(Product, on_delete=models.CASCADE)
	colour      			= models.CharField(max_length=40)

	def __str__(self):
		return self.product.name


class ProductImage(models.Model):
	'''
	this is for extra images of product
	'''
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	image 	= models.ImageField(upload_to='Product/OtherImg')

	def __str__(self):
		return self.product.name


class ProductReviews(models.Model):
	'''
	feedback of user after delivery of product
	after rating avg_rating should be change
	'''
	product             = models.ForeignKey(Product, on_delete=models.CASCADE)
	user                = models.ForeignKey(User, on_delete=models.CASCADE)
	rating              = models.PositiveIntegerField( validators=[MaxValueValidator(5), MinValueValidator(1)])
	content             = models.TextField(blank=True,null=True)
	created             = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.product.name) +' - '+str(self.user)+' - '+str(self.rating)


class CustomerProductWishList(models.Model):
	product             = models.ForeignKey(Product, on_delete=models.CASCADE)
	user                = models.ForeignKey(User, on_delete=models.CASCADE)
	selected_size       = models.CharField(blank=True,null=True,max_length=5) # customer can select size
	selected_colour     = models.ForeignKey(ProductAvailableColourWithSizeQty, null=True, blank=True,on_delete=models.SET_NULL) # if applicable            
	created           	= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.user) +' - '+str(self.product.name)


class CustomerProductCart(models.Model):
	product             = models.ForeignKey(Product, on_delete=models.CASCADE)
	user                = models.ForeignKey(User, on_delete=models.CASCADE)

	# customer selection for product
	
	selected_size       = models.CharField(max_length=10)
	selected_colour     = models.ForeignKey(ProductAvailableColourWithSizeQty, null=True, on_delete=models.SET_NULL) # if applicable            
	selected_quantity   = models.PositiveIntegerField(default=1)
	created           	= models.DateTimeField(auto_now_add=True)

	# active when product order 

	is_ordered            = models.BooleanField(default=False)

	def __str__(self):
		return str(self.user) +' - '+str(self.product.name)


TYPE_CHOICES = (
    ('1', "percent"),
    ('2', "amount"),
    )

class CouponCode(models.Model):
	code       				=  models.CharField(max_length=50, unique = True)

	coupon_type             =  models.CharField(max_length=10 ,choices=TYPE_CHOICES)
	value                   =  models.CharField(max_length=10)

	# max off by Coupon Code when type percent selected 
	max_amount              =  models.CharField(max_length=10,blank=True,null=True)

	# max time use by user

	usage_limit             =  models.CharField(max_length=2,blank=True,null=True)  

	# validity 
	valid_from 				=  models.DateField()
	valid_to    			=  models.DateField()

	# customer selection

	is_for_all_user 		=  models.BooleanField(default=False)
	selected_users          =  models.ManyToManyField(User,blank=True)

	# product selection 

	is_for_all_product      =  models.BooleanField(default=False)
	selected_product        =  models.ManyToManyField(Product,blank=True)

	# terms and condition 

	terms_and_cond          =  models.TextField()
	description             =  models.TextField()           
	created           		=  models.DateTimeField(auto_now_add=True)

	is_active               = models.BooleanField(default=False)

	def __str__(self):
		return self.code + '-' +str(self.id)



class CoupanCodeUseLimit(models.Model):
	user 	= models.ForeignKey(User ,on_delete=models.CASCADE)
	coupon  = models.ForeignKey(CouponCode ,on_delete=models.CASCADE)
	used   	= models.CharField(max_length=2)

	def __str__(self):
		return self.user.first_name + '-' +str(self.coupon)

	class Meta:
		unique_together = ('user','coupon')


class DeliveryDistanceManagement(models.Model):
	dist_from 	=  models.IntegerField()
	dist_to 	=  models.IntegerField()
	charges 	=  models.IntegerField()

	def __str__(self):
		return str(self.dist_from) + '-' + str(self.dist_to)
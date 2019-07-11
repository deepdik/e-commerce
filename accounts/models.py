from django.db import models
from django.contrib.auth.models import User 
# Create your models here.
from django.core.validators import MaxValueValidator, MinValueValidator


GENDER = (('male', 'Male'),('female','Female'))
DEVICETYPE= (('android', 'Android'),('ios','IOS'),('web','Web'))


class Role (models.Model):
	role_id 	= models.CharField(max_length=2)
	name    	= models.CharField(max_length=50)

	def __str__(self):
		return self.name + '-'+self.role_id


class UserOtherInfo(models.Model):
	user                    = models.OneToOneField(User, on_delete=models.CASCADE)
	role                    = models.ForeignKey(Role, default=1,on_delete=models.DO_NOTHING)
	isprofile_created       = models.BooleanField(default=False)
	profileimg              = models.ImageField(upload_to='user/profileimg',blank=True,null=True)
	coverimg                = models.ImageField(upload_to='user/coverimg',blank=True,null=True)
	phonenum                = models.CharField(max_length=14)
	country_code            = models.CharField(max_length=5,blank=True,null=True)
	isnumverify			 	= models.BooleanField(default =False)
	ismailverify			= models.BooleanField(default =False)
	gender                  = models.CharField(blank=True,null=True,max_length=10,choices = GENDER)
	addr_one          		= models.CharField(max_length=100,blank=True,null=True)
	addr_two          		= models.CharField(max_length=50,blank=True,null=True)
	addr_three         		= models.CharField(max_length=50,blank=True,null=True)
	device_token            = models.CharField(max_length=500,blank=True,null=True) # in doubt
	device_type             = models.CharField(max_length=20,blank=True,null=True,choices=DEVICETYPE)
	region                  = models.CharField(max_length=30,blank=True,null=True)
	rating              	= models.FloatField( blank=True,null=True,validators=[MaxValueValidator(5), MinValueValidator(1)])
	about                   = models.TextField(blank=True,null=True)
	created                 = models.DateField(auto_now_add=True)
	def __str__(self):
		return self.user.first_name + '-'+ str(self.id)

	class Meta:
		unique_together = ('phonenum','country_code')


class Permission(models.Model):
	permission_id 	= models.IntegerField(primary_key=True)
	name 			= models.CharField(max_length=50)
	des             = models.TextField(blank=True,null=True)

	def __str__(self):
		return self.name 

class UserPermissions(models.Model):
	user   		= models.ForeignKey(User, on_delete=models.CASCADE)
	permission 	= models.ManyToManyField(Permission)

	def __str__(self):
		return self.user.first_name
		


		
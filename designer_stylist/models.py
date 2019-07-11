from django.db import models
from django.contrib.auth.models import User

# Create your models here.

ROLE = (('3','designer'),('4','stylist'),('5','manufacturer'))

class Profile(models.Model):
	user                    = models.OneToOneField(User,on_delete=models.CASCADE)
	role                    = models.CharField(max_length=13,choices=ROLE)
	name 					= models.CharField(max_length=50)
	email                   = models.CharField(max_length=50)
	profileimg              = models.ImageField(upload_to='user/profile_img',blank=True,null=True)
	coverimg                = models.ImageField(upload_to='user/cover_img',blank=True,null=True)
	des                   	= models.TextField()
	product_sold       		= models.PositiveIntegerField(blank=True,null=True)
	profile_views           = models.PositiveIntegerField(blank=True,null=True)
	rating                  = models.FloatField(blank=True,null=True)

	def __str__(self):
		return self.user.first_name + '-' +str(self.user.id)


class Achievement(models.Model):
	designerprofile = 	models.ForeignKey(Profile, on_delete=models.CASCADE)
	year  			=   models.DateField(blank=True,null=True)
	title  			=   models.CharField(max_length=50)
	about           =   models.TextField(blank=True,null=True)

	def __str__(self):
		return self.designerprofile.name

class Image(models.Model):
	achievement 	= 	models.ForeignKey(Achievement, on_delete=models.CASCADE)
	image           =   models.ImageField(upload_to='user/achievement_img')

	def __str__(self):
		return str(self.achievement)


class StylistDesignerCategory(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)

	def __str__(self):
		return str(self.name)

class StylistDesignerSection(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)

	def __str__(self):
		return str(self.id) + '-' +self.name

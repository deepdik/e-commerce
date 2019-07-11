from django.db import models
from django.contrib.auth.models import User




class ReturnAndRefundPloicy(models.Model):
	return_policy 	= models.TextField(blank=True)
	refund_policy  	= models.TextField(blank=True)
	created  		= models.DateTimeField(auto_now_add=True)


class ContactAboutTerms(models.Model):
	about_us 		= models.TextField(blank=True,null=True)
	terms  			= models.TextField(blank=True,null=True)
	contact_us  	= models.TextField(blank=True,null=True)
	created  		= models.DateTimeField(auto_now_add=True)
	last_update  	= models.DateTimeField(auto_now=True)


class Faq(models.Model):
	query 			= models.TextField(blank=True,null=True)
	answer  		= models.TextField(blank=True,null=True)
	created  		= models.DateTimeField(auto_now_add=True)
	last_update  	= models.DateTimeField(auto_now=True)

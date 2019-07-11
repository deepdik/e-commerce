from django.core.exceptions import PermissionDenied
from  . models import UserOtherInfo,UserPermissions
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from ifashionup import settings
from django.shortcuts import render



def staff_user_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = self.request.user

		# check user login
		if not user.is_authenticated:
			return HttpResponseRedirect(settings.LOGIN_URL)

		# if user is not from stylist,designer, manufacturer 
		
		if user.is_staff:
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')

	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap


def admin_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		login_user = UserOtherInfo.objects.get(user= self.request.user)
		if login_user.role =='2':
			return function(request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap


def dashboard_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=1)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def dashboard_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=1)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def account_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=2)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def member_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=3)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def chat_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=4)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def order_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=5)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def payment_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=6)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def report_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=7)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def product_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=8)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

 
def category_permission_required(function): # stylist designer  manufacturer
	def wrap(self,request, *args, **kwargs):

		user = request.user
		# if user is not from stylist,designer, manufacturer 
		qs = UserPermissions.objects.filter(user=user, permission=8)
		if qs.exists():
			return function(self,request, *args, **kwargs)
		else:
			return render(request,'errors/staff_user_required.html')
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap


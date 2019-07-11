from django import forms
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User
from designer_stylist.models import *
from accounts.models import UserOtherInfo

from product.models import DeliveryDistanceManagement,CouponCode


class LoginForm(forms.Form):
	email = forms.CharField()
	password = forms.CharField()
	


	def clean(self):
		email = self.cleaned_data.get('email')
		userA =User.objects.filter(email=email)
		user = userA.exclude(email__isnull=True).exclude(email__iexact='').distinct()
		if user.exists() and user.count() == 1:
			userObject = user.first()
		else:
			raise forms.ValidationError("User with this E-mail is not exist")
		password = self.cleaned_data.get('password')
		check_pass = userObject.check_password(password)
		if check_pass:
			if not userObject.is_staff or not userObject.is_active:
				raise forms.ValidationError('Your have not permission to access this panel')
			return self.cleaned_data
		raise forms.ValidationError('Your password is incorrect')


class ChangePasswordForm(forms.Form):
	oldpassword 	= forms.CharField()
	password 		= forms.CharField()
	confpassword 	= forms.CharField()
	
	def __init__(self, *args, **kwargs):
		 self.user = kwargs.pop('user',None)
		 super(ChangePasswordForm, self).__init__(*args, **kwargs)
		 self.fields['oldpassword'].strip = False
		 self.fields['password'].strip = False
		 self.fields['confpassword'].strip = False

	def clean(self):
		password = self.cleaned_data.get('password')
		confpassword =self.cleaned_data.get('confpassword')

		print(len(password))
		if not len(password) >= 8 or not len(confpassword) >= 8:

			raise forms.ValidationError('Password must be at least 8 characters')

		oldpassword = self.cleaned_data.get('oldpassword')
		if not self.user.check_password(oldpassword):
			raise forms.ValidationError('Incorrect old password')

		if password!=confpassword:
			raise forms.ValidationError('Both password fields should be same')

		
		
		return self.cleaned_data


class AdminProfileEditForm(forms.Form):
	email 		= forms.CharField()
	phonenumber = forms.CharField()
	address 	= forms.CharField()	
	about 		= forms.CharField()
	firstname 	= forms.CharField()
	lastname 	= forms.CharField()

	def __init__(self, *args, **kwargs):
		 self.user = kwargs.pop('user',None)
		 super(AdminProfileEditForm, self).__init__(*args, **kwargs)

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if not self.user.email == email: 
			
			if email.count('@')>1:
				raise forms.ValidationError('Please enter a valid email')
			try:
				domain = email.split("@")[1]
			except:
				raise forms.ValidationError('Please enter a valid email')

			user_qs = User.objects.filter(email__iexact = email)

			if user_qs.exists():
				raise forms.ValidationError('User with this Email already exist')
			return email

		return email


	def clean_phonenumber(self):
		
		phonenumber = self.cleaned_data.get('phonenumber')
		
		if phonenumber.isdigit() and len(phonenumber)<12:           
			obj = UserOtherInfo.objects.get(user = self.user)
			if not obj.phonenum==phonenumber:
				user_qs = UserOtherInfo.objects.filter(phonenum__iexact=phonenumber)
				if user_qs.exists():
					raise forms.ValidationError('User with this phone number already exist')
				return phonenumber
			return phonenumber
		raise forms.ValidationError('Please correct your Mobile number')




class AddMemberForm(forms.Form):
	firstname   = forms.CharField()
	lastname   	= forms.CharField()
	gender   	= forms.CharField()
	email 		= forms.CharField()
	countrycode = forms.CharField()
	phonenumber = forms.CharField()
	region 		= forms.CharField()	
	addr_1 		= forms.CharField()
	addr_2 		= forms.CharField()
	addr_3 		= forms.CharField()
	status      = forms.CharField()
	role      	= forms.CharField()
	password    = forms.CharField()



	def clean_email(self):
		email = self.cleaned_data.get('email')
		user_qs = User.objects.filter(email__iexact = email)
		if user_qs.exists():
			raise forms.ValidationError('User with this Email already exists')
		return email

	def clean_phonenumber(self):
		phonenumber = self.cleaned_data.get('phonenumber')
		user_qs = UserOtherInfo.objects.filter(phonenum = phonenumber)
		if user_qs.exists():
			raise forms.ValidationError('User with this phone number already exists')
		return phonenumber

	def clean_password(self):
		password = self.cleaned_data.get('password')
		if len(password) < 8:
			raise forms.ValidationError('Password must be at least 8 characters')
		return password
	



class AdminMemberEditForm(forms.Form):
	firstname   = forms.CharField()
	lastname   	= forms.CharField()
	gender   	= forms.CharField()
	email 		= forms.CharField()
	countrycode = forms.CharField()
	phonenumber = forms.CharField()
	address 	= forms.CharField(required = False)
	status      = forms.CharField()
	# role      	= forms.CharField()

	def __init__(self,*args, **kwargs):
		self.user_id = kwargs.pop('user_id',None)

		super(AdminMemberEditForm, self).__init__(*args, **kwargs)

	
	def clean_email(self):
		email = self.cleaned_data.get('email')
		obj = UserOtherInfo.objects.select_related('user').get(pk =self.user_id)
		if not obj.user.email == email: 
			allowedDomains = [
			"aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
			"google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
			"live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
			"email.com", "games.com" , "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
			"lavabit.com", "love.com" , "outlook.com", "pobox.com", "rocketmail.com",
			"safe-mail.net", "wow.com", "ygm.com" , "ymail.com", "zoho.com", "fastmail.fm",
			"yandex.com","iname.com","fluper.in"
			]
			if email.count('@')>1:
				raise forms.ValidationError('Please enter a valid email')
			try:
				domain = email.split("@")[1]
			except:
				raise forms.ValidationError('Please enter a valid email')

			if domain not in allowedDomains:
				raise forms.ValidationError('Please enter a valid email')

			user_qs = User.objects.filter(email__iexact = email)

			if user_qs.exists():
				raise forms.ValidationError('User with this Email already exist')
			return email

		return email


	def clean_phonenumber(self):
		
		phonenumber = self.cleaned_data.get('phonenumber')
		
		if phonenumber.isdigit() and len(phonenumber)<12:           
			obj = UserOtherInfo.objects.get(pk = self.user_id)
			if not obj.phonenum==phonenumber:
				user_qs = UserOtherInfo.objects.filter(phonenum__iexact=phonenumber)
				if user_qs.exists():
					raise forms.ValidationError('User with this phone number already exist')
				return phonenumber
			return phonenumber
		raise forms.ValidationError('Please correct your Mobile number')



class AppInProfileCreateForm(forms.Form):
	name        = forms.CharField(error_messages={'required': 'Please enter your name'})
	email   	= forms.EmailField(error_messages={'required': 'Please enter your email'})
	year        = forms.CharField()
	title       = forms.CharField()
	about       = forms.CharField(error_messages={'required': 'Please describle yourself'})
	profileimg  = forms.FileField(error_messages={'required': 'Please choose a profile image'})
	coverimg    = forms.FileField(error_messages={'required': 'Please choose a cover image'})
	achievement_images = forms.FileField(error_messages={'required': 'Please choose awards images'})
	
	def __init__(self, *args, **kwargs):		
		super(AppInProfileCreateForm, self).__init__(*args, **kwargs)
		self.fields['name'].strip = False
		self.fields['year'].strip = False
		self.fields['title'].strip = False
		self.fields['about'].strip = False
		self.fields['email'].strip = False

	def clean(self):
		if self.cleaned_data.get('name').strip()== '' or self.cleaned_data.get('email').strip()=='' or self.cleaned_data.get('title').strip()=='' or self.cleaned_data.get('about').strip() == '':
			raise forms.ValidationError('Whitespaces are not allowed in input fields')
		return self.cleaned_data



class AppInProfileEditForm(forms.Form):
	name        = forms.CharField(error_messages={'required': 'Please enter your name'})
	email   	= forms.EmailField(error_messages={'required': 'Please enter your email'})
	year        = forms.CharField()
	title       = forms.CharField()
	about       = forms.CharField(error_messages={'required': 'Please describle yourself'})
	
	def __init__(self, *args, **kwargs):
		 
		super(AppInProfileEditForm, self).__init__(*args, **kwargs)
		self.fields['name'].strip = False
		self.fields['year'].strip = False
		self.fields['title'].strip = False
		self.fields['about'].strip = False
		self.fields['email'].strip = False
	
	def clean(self):
		if self.cleaned_data.get('name').strip()== '' or self.cleaned_data.get('email').strip()=='' or self.cleaned_data.get('title').strip()=='' or self.cleaned_data.get('about').strip() == '':
			raise forms.ValidationError('Whitespaces are not allowed in input fields')
		return self.cleaned_data




class StylistDesignerSectionForm(forms.ModelForm):

	class Meta:
		model = StylistDesignerSection
		fields = ['name']


class StylistDesignerCategoryForm(forms.ModelForm):

	class Meta:
		model = StylistDesignerCategory
		fields = ['name']



class OldProductCreateForm(forms.Form):
	name        	= forms.CharField()
	category   		= forms.CharField()
	subcategory     = forms.CharField()
	subsubcategory  = forms.CharField()
	owncategory    	= forms.CharField(required=False)
	des        		= forms.CharField()
	material        = forms.CharField(required=True)
	fit        		= forms.CharField(required=True)
	offer_price   	= forms.IntegerField(required=False)
	quantity     	= forms.IntegerField()
	price  			= forms.IntegerField()
	size			= forms.CharField(error_messages={'required': 'Please select sizes of Product'})
	# main_img    	= forms.FileField(error_messages={'required': 'Please choose a main image of Product'})

	def __init__(self, *args, **kwargs):
		 
		super(ProductCreateForm, self).__init__(*args, **kwargs)
		self.fields['name'].strip = False
		self.fields['des'].strip = False
		self.fields['material'].strip = False
		self.fields['fit'].strip = False
		
	def clean(self):
		if self.cleaned_data.get('name').strip()== '' or self.cleaned_data.get('des').strip()=='' or self.cleaned_data.get('material').strip()=='' or self.cleaned_data.get('fit').strip() == '':
			raise forms.ValidationError('Whitespaces are not allowed in input fields')
		return self.cleaned_data


class ProductCreateForm(forms.Form):
	name        	= forms.CharField()
	category   		= forms.CharField()
	subcategory     = forms.CharField()
	subsubcategory  = forms.CharField()
	# owncategory    	= forms.CharField(required=False)
	des        		= forms.CharField()
	more_info       = forms.CharField(required=False)
	is_active       = forms.CharField(required=False)
	material        = forms.CharField()
	new_from        = forms.CharField(required=False)
	new_to	        = forms.CharField(required=False)
	fit        		= forms.CharField()
	pattern         = forms.CharField(required=False)

	def __init__(self, *args, **kwargs):	 
		super(ProductCreateForm, self).__init__(*args, **kwargs)
		self.fields['name'].strip = False
		self.fields['des'].strip = False
		self.fields['material'].strip = False
		self.fields['fit'].strip = False
		self.fields['more_info'].strip = False
		
	def clean(self):
		print(self.cleaned_data.get('name'))
		if self.cleaned_data.get('name').strip()== '' or  self.cleaned_data['des'].strip()== '' or self.cleaned_data['more_info'].strip()== '' or self.cleaned_data['material'].strip()== '' or self.cleaned_data['fit'].strip()== '' or self.cleaned_data['pattern'].strip()== '' :
			raise forms.ValidationError('Whitespaces are not allowed in input fields')
		return self.cleaned_data

class AddProductVarientsForm(forms.Form):
	colour        	= forms.CharField()
	price   		= forms.IntegerField()
	special_price     = forms.IntegerField(required=False)
 

	def clean(self):
		print(self.cleaned_data.get('name'))
		if self.cleaned_data.get('special_price') != '':
			if self.cleaned_data['price'] < self.cleaned_data['special_price']:
				raise forms.ValidationError('Offer price can not  be greater than price(MRP) ')
		return self.cleaned_data


class CouponAddForm(forms.Form):
	code        	= forms.CharField(strip=False)
	coupon_type   	= forms.CharField()
	value     		= forms.IntegerField()
	max_amount  	= forms.IntegerField(required=False)
	usage_limit     = forms.CharField()
	valid_to        = forms.CharField()
	valid_from    	= forms.CharField()
	terms        	= forms.CharField()
	description   	= forms.CharField()

	def __init__(self, *args, **kwargs):
		 
		super(CouponAddForm, self).__init__(*args, **kwargs)
		self.fields['code'].strip = False
		self.fields['value'].strip = False
		self.fields['max_amount'].strip = False
		self.fields['terms'].strip = False
		self.fields['description'].strip = False

	def clean(self):
		if self.cleaned_data.get('code').strip()== '' or self.cleaned_data.get('terms').strip()=='' or self.cleaned_data.get('description').strip()=='':
			raise forms.ValidationError('Whitespaces are not allowed in input fields')

		return self.cleaned_data
		

class DeliveryChargesForm(forms.Form):
	dist_from 	= forms.IntegerField()
	dist_to 	= forms.IntegerField()
	charge 		= forms.IntegerField()


	def __init__(self,*args, **kwargs):
		self.id = kwargs.pop('id',None)

		super(DeliveryChargesForm, self).__init__(*args, **kwargs)

	def clean(self):
		dist_from = self.cleaned_data.get('dist_from')
		dist_to = self.cleaned_data.get('dist_to')

		obj = DeliveryDistanceManagement.objects.get(id=self.id)

		if obj.dist_from == dist_from and obj.dist_to == dist_to:
			return self.cleaned_data
		else:

			qs = DeliveryDistanceManagement.objects.filter(dist_from__range=(dist_from,dist_to)).exclude(id=obj.id)
			print(qs)

			if qs.exists():
				obj = qs.first()
				raise forms.ValidationError('This distance is already included in '+  str(obj) )

			qs = DeliveryDistanceManagement.objects.filter(dist_to__range=(dist_from,dist_to)).exclude(id=obj.id)

			print(qs)
			if qs.exists():
				obj = qs.first()
				raise forms.ValidationError('This distance is already included in '+  str(obj))


			if self.cleaned_data.get('dist_from')== self.cleaned_data.get('dist_to'):
				raise forms.ValidationError('Both distance fields should not be same')

			if self.cleaned_data.get('dist_from') > self.cleaned_data.get('dist_to'):
				raise forms.ValidationError('Distance from should be less than distance to')


			return self.cleaned_data

class DeliveryChargesAddForm(forms.Form):
	dist_from 	= forms.IntegerField()
	dist_to 	= forms.IntegerField()
	charge 		= forms.IntegerField()

	def clean(self):
		dist_from = self.cleaned_data.get('dist_from')
		dist_to = self.cleaned_data.get('dist_to')

		qs = DeliveryDistanceManagement.objects.filter(dist_from__range=(dist_from,dist_to))
		print(qs)

		if qs.exists():
			obj = qs.first()
			raise forms.ValidationError('This distance is already included in '+  str(obj) )

		qs = DeliveryDistanceManagement.objects.filter(dist_to__range=(dist_from,dist_to))

		print(qs)
		if qs.exists():
			obj = qs.first()
			raise forms.ValidationError('This distance is already included in '+  str(obj))


		if self.cleaned_data.get('dist_from')== self.cleaned_data.get('dist_to'):
			raise forms.ValidationError('Both distance fields should not be same')

		if self.cleaned_data.get('dist_from') > self.cleaned_data.get('dist_to'):
			raise forms.ValidationError('Distance from should be less than distance to')


		return self.cleaned_data



from .models import ReturnAndRefundPloicy,Faq

def is_whitespaces(string):
	string_a = string.replace('&nbsp;', '')
	string_b = 	string_a.replace('<p>' , '')
	string_c = 	string_b.replace('</p>' , '')
	string_d = string_c.replace('\r\n' , '')
	string_e = string_d.strip()
	print(string_e,'sdfggggggggggg')
	if string_e =='':
		return True
	else:
		return False



class ReturnAndRefundPolicyForm(forms.Form):
	return_policy 	= forms.CharField(required=False)
	refund_policy 	= forms.CharField(required=False)

	def clean(self):

		if self.cleaned_data.get('return_policy')=='':
			raise forms.ValidationError('Return &  exchange policy field is required')

		if self.cleaned_data.get('refund_policy')=='':
			raise forms.ValidationError('Refund policy field is required')

		if is_whitespaces(self.cleaned_data.get('refund_policy')) or is_whitespaces(self.cleaned_data.get('return_policy')):
			raise forms.ValidationError('Whitespaces are not allowed in input fields')

		return self.cleaned_data



class ContactAboutTermsForm(forms.Form):
	about_us 	= forms.CharField(required=False)
	terms 		= forms.CharField(required=False)
	contact_us 	= forms.CharField(required=False)


	def __init__(self, *args, **kwargs):
		 
		super(ContactAboutTermsForm, self).__init__(*args, **kwargs)
		self.fields['about_us'].strip = False
		self.fields['terms'].strip = False
		self.fields['contact_us'].strip = False

	def clean(self):
		if not self.cleaned_data.get('about_us') == '':
			if is_whitespaces(self.cleaned_data.get('about_us')):
				raise forms.ValidationError('Whitespaces are not allowed in input fields')
		if not self.cleaned_data.get('terms') == '':
			if is_whitespaces(self.cleaned_data.get('terms')):
				raise forms.ValidationError('Whitespaces are not allowed in input fields')
		if not self.cleaned_data.get('contact_us') == '':
			if is_whitespaces(self.cleaned_data.get('contact_us')):
				raise forms.ValidationError('Whitespaces are not allowed in input fields')
		if self.cleaned_data.get('about_us') == '' and self.cleaned_data.get('terms') == '' and self.cleaned_data.get('contact_us') == '':
			raise forms.ValidationError('Please fill at least one field')

		return self.cleaned_data


class FaqForm(forms.Form):

	query        	= forms.CharField()
	answer   		= forms.CharField()

	def __init__(self, *args, **kwargs):
		 
		super(FaqForm, self).__init__(*args, **kwargs)
		self.fields['query'].strip = False
		self.fields['answer'].strip = False

	def clean(self):
		if self.cleaned_data.get('answer').strip()== '' or self.cleaned_data.get('query').strip()=='':
			raise forms.ValidationError('Whitespaces are not allowed in input fields')

		return self.cleaned_data


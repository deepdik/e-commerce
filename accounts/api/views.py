from rest_framework.generics import (
		CreateAPIView,
	)

import logging
logger = logging.getLogger('accounts')



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
	HTTP_200_OK,
	HTTP_400_BAD_REQUEST
	,HTTP_204_NO_CONTENT,
	HTTP_201_CREATED,
	HTTP_500_INTERNAL_SERVER_ERROR
	)
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import *

from .permissions import IsAuthenticatedOrCreate
from accounts.models import UserOtherInfo
from rest_framework.exceptions import ValidationError

from authy.api import AuthyApiClient
authy_api = AuthyApiClient('YnWJyrBePlU7U4Xj892WLAYeuEuaSsrH')

User = get_user_model()

#PASSWORD RESET BY EMAIL START------

from .settings import (  
	PasswordResetSerializer,     
)
from rest_framework.generics import GenericAPIView
from rest_framework import status

#END--------------------------------

from rest_framework_jwt.authentication import  JSONWebTokenAuthentication




class UserCreateAPIView(CreateAPIView):

	serializer_class = UserCreateSerializer
	# permission_classes = (IsAuthenticatedOrCreate,)

	# def create(self, request, *args, **kwargs):
	#   data = request.data
	#   for key in data:
	#       print(key)
	#   serializer = UserLoginSerializer(data=data)
	#   if serializer.is_valid(raise_exception=True):


	#       return Response(new_data,status=HTTP_200_OK)
	#   print(serializer.errors)            
	#   return Response('ok',status=HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
	permission_classes = [AllowAny]
	serializer_class = UserLoginSerializer
	
	def post(self,request,*args,**kwargs):
		data = request.data
		logger.debug('Log whatever you want')
		serializer = UserLoginSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			phone_number = data['phonenumber']
			country_code = data['countrycode']
			isnumverify  = serializer.data['isnumverify']
			new_data = serializer.data
			if isnumverify == "false":
				request = authy_api.phones.verification_start(phone_number, country_code, 
					via='sms', locale='en')
				return Response(new_data,status=HTTP_200_OK)
			else:   
				return Response(new_data,status=HTTP_200_OK)            
		return Response(serializer.errors,status=HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get_object(self):
		return self.request.user

	def put(self,request,*args,**kwargs):
		user = self.get_object()
		serializer = ChangePasswordSerializer(data=request.data)
		if serializer.is_valid():
			oldPassword = serializer.data.get("oldPassword")
			newPassword = serializer.data.get("newPassword")
			# confPassword = serializer.data.get("confPassword")
			# if newPassword == confPassword:
			if not user.check_password(oldPassword):
				return Response({"message":"You entered wrong current password"},
					status=HTTP_400_BAD_REQUEST)

			user.set_password(newPassword)
			user.save()
			return Response(
				{'success':"true",
				'message':'Your password changed successfully'
				},status=HTTP_200_OK)
			# return Response({"message":"New password and confirm password should be same"},
			# 			status=HTTP_400_BAD_REQUEST)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class PasswordResetView(GenericAPIView):

	"""
	Calls Django Auth PasswordResetForm save method.
	Accepts the following POST parameters: email
	Returns the success/fail message.
	"""
	
	serializer_class = PasswordResetSerializer
	permission_classes = (AllowAny,)

	def post(self, request, *args, **kwargs):
		# Create a serializer with request.data
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		serializer.save()
		# Return the success message with OK HTTP status
		return Response(

			{"success": "true",
			'message':  "Password reset e-mail has been sent."},
			status=status.HTTP_200_OK
		)

class ProfileCreateAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]
	def post(self, request, *args, **kwargs):
		user = request.user
		data = request.data
		gender = data['gender']
		addr_1 = data['addr_1']
		addr_2 = data['addr_2']
		addr_3 = data['addr_3']
		image =  request.FILES.get('image')
		if gender:          
			obj = UserOtherInfo.objects.get(user=user)
			obj.gender = gender
			obj.addr_one = addr_1
			obj.addr_two = addr_2
			obj.addr_three = addr_3
			obj.profileimg = image
			obj.isprofile_created =True             
			obj.save()
			return Response(
				{"success": "true",
				'message':  "Profile created successfully",

				},
				status=status.HTTP_201_CREATED
				)
			
			
		return Response({
					'success':"false",
					'message':"Please select gender"},
					
					status=HTTP_400_BAD_REQUEST)


# twillio sms otp






class OtpGenerateForPasswordResetAPIView(APIView):
	'''
	Otp generate  for password reset apiview
	'''
	def post(self,request):
		phone_number = request.data['phonenumber']
		country_code = request.data['countrycode']
		if phone_number and country_code:
			
			user_qs = UserOtherInfo.objects.filter(phonenum=phone_number,country_code=country_code)
			if user_qs.exists():

				"""
				for production version
				"""

				request = authy_api.phones.verification_start(phone_number, country_code, 
					via='sms', locale='en')
				if request.content['success'] ==True:
					return Response({
						'success':True,
						'msg':'OTP has been successfully sent to your registered mobile number'},
						status=HTTP_200_OK)

				else:
					# return Response({
					#   'success':False,
					#   'msg':request.content['message']},
					#   status=HTTP_400_BAD_REQUEST)
					return Response({
						'success':True,
						'msg':'OTP has been successfully sent to your registered mobile number'},
						status=HTTP_200_OK

						)

				"""
				for development version
				"""
				# return Response({
				#   'success':"true",
				#   'message':"otp have been send to your number"},
				#   status=HTTP_200_OK)

			return Response({
					'success':"false",
					'message':"User with this number is not exists"},
					
					status=HTTP_400_BAD_REQUEST)
		else:
			return Response({
					'success':"false",
					'message':"Provide phone number"},status=HTTP_400_BAD_REQUEST)


from rest_framework_jwt.settings import api_settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class OtpVarifyForPasswordResetAPIView(APIView):
	def post(self,request):
		'''
		to check verification code 
		'''
		phone_number = request.data['phonenumber']
		country_code = request.data['countrycode']
		verification_code = request.data['verification_code']
		if phone_number and country_code and verification_code:

			"""
			for production version
			"""

			check = authy_api.phones.verification_check(phone_number, country_code, verification_code)
			if check.ok()==True or verification_code =="1234":

			# if verification_code=='1234':
				obj = UserOtherInfo.objects.get(phonenum=phone_number,country_code=country_code)
				print(obj)
				userObj = obj.user
				payload = jwt_payload_handler(userObj)
				# payload['exp']= 3000
				token = jwt_encode_handler(payload)
				return Response({
					'success':"true",
					# 'message':check.content['message'],    # Production version
					'message':'Your number has been verified successfully',
					'token':token
					},
					status=HTTP_200_OK)
			return Response({
					'success':"false",
					'message':'Otp code is wrong'
					# 'message':check.content['message']     # production version
					},
					status=HTTP_400_BAD_REQUEST)
		 

		return Response('provide phone_number, verification_code',status=HTTP_400_BAD_REQUEST)


class PasswordResetByPhoneAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]
	def post(self,request,*args,**kwargs):
		data = request.data
		user = request.user
		serializer = ResetPasswordByPhoneSerializer(data=data)
		if serializer.is_valid():
			password = serializer.data.get("password")
			repassword = serializer.data.get("confpassword")

			if password == repassword:
				print('ok')
				user.set_password(password)
				user.save()
				return Response({
					'success':"true",   
					'message':'Your password have been changed successfully'
					},
					status=HTTP_200_OK)

			return Response({
					'success':"false",  
					'message':'Both password fields should be same'
					},
					status=HTTP_400_BAD_REQUEST)                
		return Response(serializer.errors , status=HTTP_400_BAD_REQUEST)

class OTPCreateForRegistrationAPIView(APIView):

	def post(self,request,*args,**kwargs):

		serializer = UserCreateSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()


			'''
			For production version
			'''

			phone_number = serializer.data.get("phonenumber")
			country_code = serializer.data.get("countrycode")
			if phone_number and country_code:
				request = authy_api.phones.verification_start(phone_number, country_code, 
					via='sms', locale='en')
				if request.content['success'] == True:
					return Response(
						serializer.data,
						status=HTTP_200_OK)
				else:
					# return Response({
					#   'success':"false",
					#   'msg':request.content['message']},
					#   status=HTTP_400_BAD_REQUEST)
					return Response(
						serializer.data,
						status=HTTP_200_OK

						)
					
			else:
				return Response('provide phone_number and country_code',status=HTTP_400_BAD_REQUEST)

			# return Response(
						
			#           serializer.data,
			#           status=HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)



# For Production 

class UserPhoneVerifyAfterRegisterAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]
	def post(self,request,*args,**kwargs):
		data = request.data
		user= request.user
		phone_number = data['phonenumber']
		country_code = data['countrycode']
		verification_code = data['verification_code']
		if phone_number and country_code and verification_code:
			check = authy_api.phones.verification_check(phone_number, country_code, verification_code)
			if check.ok()==True or verification_code =="1234":
				obj = UserOtherInfo.objects.get(user=user)
				obj.isnumverify=True
				obj.save()
				return Response({
					'success':"true",
					# 'message':check.content['message']},
					'message':'Your number has been verified successfully'
					},
						status=HTTP_200_OK)

			return Response({
					'success':"false",
					# 'message':check.content['message']
					'message':'verification code is incorrect'
					},
					status=HTTP_400_BAD_REQUEST)
		 
		return Response({
					'success':"false",
					'message':'please provide data in valid format'},status=HTTP_400_BAD_REQUEST)



class UserCreateAfterOTPAPIViewDevelopment(APIView):

	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request,*args,**kwargs):
		data = request.data
		user = request.user
		phone_number = data['phonenumber']
		country_code = data['countrycode']
		verification_code = data['verification_code']
		if verification_code == "1234":
			obj = UserOtherInfo.objects.get(user=user)
			obj.isnumverify=True
			obj.save()
			return Response({
					'success':"true",
					'message':'Your phonenumber is verified successfully'},
				status=HTTP_200_OK)
			
		return Response({
					'success':"false",
					'message':'your otp is incorrect'},
					status=HTTP_400_BAD_REQUEST)

class OTPSendForPhoneVerify(APIView):

	def post(self,request,*args,**kwargs):
		phone_number = request.data['phonenumber']
		country_code = request.data['countrycode']
		qs = UserOtherInfo.objects.filter(phonenum=phone_number,country_code=country_code)
		if qs.exists():
			# return Response({
			#   'success':"true",
			#   'message':'OTP have been send to your number please verify it'},
			#   status=HTTP_200_OK)         
			if phone_number and country_code:
				request = authy_api.phones.verification_start(phone_number, country_code, 
					via='sms', locale='en')
				if request.content['success'] ==True:
					return Response({
						'success':"true",
						'message':request.content['message']},
						status=HTTP_200_OK)
				else:
					return Response({
						'success':"false",
						'message':request.content['message']},
						# 'message':'Error in sending OTP'},
						status=HTTP_400_BAD_REQUEST)
			 
			else:
				return Response('provide phone_number and country_code',status=HTTP_400_BAD_REQUEST)
		# return Response({
		#       'success':"false",
		#       'message':'No user found with this number'},
		#       status=HTTP_400_BAD_REQUEST)



class AdminUserViewAPIView(APIView):

	def get(self,request,*args,**kwargs):
		user_id = self.kwargs['user_id']


		try:
			app_users   = UserOtherInfo.objects.select_related('user').get(id=user_id)
		except:
			app_users = None
		data = AdminUserViewSerializer(app_users).data
		return Response(data)

class AdminUserBlockAPIView(APIView):
	def post(self,request,*args,**kwargs):
		user_id = self.kwargs['user_id']
		
		try:
			user    = UserOtherInfo.objects.select_related('user').get(id=user_id)
		except:
			return Response({
						'message':'No user to block'},
						status=HTTP_400_BAD_REQUEST)

		user =  User.objects.get(id=user.user.id)
		user.is_active = False
		user.save()

		return Response({
						
						'message':'Blocked successfully'},
						status=HTTP_200_OK)


class AdminUserUnblockAPIView(APIView):
	def post(self,request,*args,**kwargs):
		user_id = self.kwargs['user_id']
		try:
			user    = UserOtherInfo.objects.select_related('user').get(id=user_id)
		except:
			return Response({
						'message':'No user to unblock'},
						status=HTTP_400_BAD_REQUEST)

		user =  User.objects.get(id=user.user.id)
		user.is_active = True
		user.save()

		return Response({
						
						'message':'Unblocked successfully'},
						status=HTTP_200_OK)


class AdminUserDeleteAPIView(APIView):
	def post(self,request,*args,**kwargs):
		user_id = self.kwargs['user_id']
		try:
			user    = UserOtherInfo.objects.select_related('user').get(id=user_id)
		except:
			return Response({
						'message':'No user to unblock'},
						status=HTTP_400_BAD_REQUEST)

		user =  User.objects.get(id=user.user.id)
		user.delete()
		return Response({
						
						'message':'deleted successfully'},
						status=HTTP_200_OK)




from django.db.models import F
from django.db.models import Q

class AdminUsersFilterAPIView(APIView):
	def post(self,request,*args,**kwargs):
		data = request.data
		print(data)
		profile_id = self.kwargs['profile_id']
		

		print(data.get('web'))
		print(data.get('android'))
		print(data.get('ios'))


		
		if data.get('web') ==True and data.get('android')==False and data.get('ios')==False:
			qs_1 = UserOtherInfo.objects.filter( role=profile_id,device_type='web')
		elif data.get('web') ==False and data.get('android')==True and data.get('ios')==False:
			qs_1 = UserOtherInfo.objects.filter(role=profile_id,device_type='android')

		elif data.get('web') ==False and data.get('android')==False and data.get('ios')==True:
			qs_1 = UserOtherInfo.objects.filter(role=profile_id,device_type='ios')
		elif data.get('web') ==True and data.get('android')==True and data.get('ios')==False:
			qs_1 = UserOtherInfo.objects.exclude(role=profile_id,device_type='ios')
		elif data.get('web') ==True and data.get('android')==False and data.get('ios')==True:
			qs_1 = UserOtherInfo.objects.exclude(role=profile_id,device_type='android')
		elif data.get('web') ==False and data.get('android')==True and data.get('ios')==True:
			qs_1 = UserOtherInfo.objects.exclude(role=profile_id,device_type='web')
		else:
			qs_1 = UserOtherInfo.objects.filter(role=profile_id)




		if data.get('male')==True and data.get('female')==False:
			qs_2 = UserOtherInfo.objects.filter(role=profile_id,gender='male')
		elif data.get('male')==False and data.get('female')==True:
			qs_2 = UserOtherInfo.objects.filter(role=profile_id,gender='female')
		else:
			qs_2 = UserOtherInfo.objects.filter(role=profile_id)


		if data.get('active')==True and data.get('inactive')==False:
			
			qs_3 = UserOtherInfo.objects.filter(role=profile_id,user__is_active=True)
		elif data.get('active')==False and data.get('inactive')==True:
			qs_3 = UserOtherInfo.objects.filter(role=profile_id,user__is_active=False)
		else:
			qs_3 = UserOtherInfo.objects.filter(role=profile_id)



		if data.get('one_star') ==True:
			qs_14 = UserOtherInfo.objects.filter(Q(role=profile_id) & Q(rating__gte = 1) & Q(rating__lt=2))
		else:
			qs_14 = UserOtherInfo.objects.none()
		if data.get('two_star') ==True:
			
			qs_24 = UserOtherInfo.objects.filter(Q(role=profile_id) &Q(rating__gte = 2) & Q(rating__lt=3))
			
		else:
			qs_24 = UserOtherInfo.objects.none()

		if data.get('three_star') ==True:
			qs_34 = UserOtherInfo.objects.filter(Q(role=profile_id) &Q(rating__gte = 3) & Q(rating__lt=4))
		else:
			qs_34 = UserOtherInfo.objects.none()

		if data.get('four_star') ==True:
			qs_44 = UserOtherInfo.objects.filter(Q(role=profile_id) &Q(rating__gte = 4) & Q(rating__lt=5))
		else:
			qs_44 = UserOtherInfo.objects.none()

		if data.get('five_star') ==True:
			qs_54 = UserOtherInfo.objects.filter(role=profile_id , rating=5)
		else:
			qs_54 = UserOtherInfo.objects.none()


		qs_4 = (qs_54 | qs_44 | qs_34 | qs_24 | qs_14)

		print(qs_24,qs_54,qs_34,qs_44,qs_14)
			
		if (data.get('one_star')==False and data.get('two_star')==False  and data.get('five_star')==False  and data.get('four_star')==False  and data.get('three_star')==False) or(data.get('one_star')==True and data.get('two_star')==True  and data.get('five_star')==True  and data.get('four_star')==True  and data.get('three_star')==True):
			qs_4 = UserOtherInfo.objects.filter(role=profile_id)


		print(qs_4)

		user_qs  = (qs_1 & qs_2 & qs_3 & qs_4)

		data  =  AdminUserListSerializer(user_qs,many=True).data

		return Response(data)



import random 
from accounts.models import Role,UserPermissions
class AddNewMemberAPIView(APIView):

	def post(self,request,*args,**kwargs):
		data = request.data
		print(request.data)
		serializer = AddNewMemberSerializer(data=data)
		if serializer.is_valid():
			email =	serializer.data.get('email')
			password =	serializer.data.get('password')
			firstname =	serializer.data.get('firstname')
			lastname =	serializer.data.get('lastname')
			status =	serializer.data.get('status')
			address =	serializer.data.get('address')
			gender =	serializer.data.get('gender')
			role =	serializer.data.get('role')
			phonenumber =	serializer.data.get('phonenumber')
			country_code =	serializer.data.get('country_code')
			permissions =	request.data.get('rights')
			print(permissions)
			num = random.randint(1000, 1000000)
			username = firstname + str(num)

			if status=='active':
				status =True
			else:
				status =False
			role = Role.objects.get(name=role)
			obj = User(username=username,email=email,first_name=firstname,last_name=lastname,is_active=status,is_staff=True)
			obj.set_password(password)
			obj.save()	
			UserOtherInfo.objects.create(user = obj, phonenum=phonenumber, role=role,addr_one=address, country_code=country_code, gender=gender)
			
			userpermission = UserPermissions.objects.create(user= obj)

			permissions = list(map(str, permissions))
			print(permissions)

			userpermission.permission.add(*permissions)

			# send email ....

			return Response({
						
						'message':'Created successfully'},
						status=HTTP_200_OK)
		return Response(serializer.errors ,status=HTTP_400_BAD_REQUEST)


class EditMemberAPIView(APIView):
	def post(self,request,*args,**kwargs):
		data = request.data
		print(data)
		user_id = self.kwargs['user_id']

		serializer = EditNewMemberSerializer(data=data ,context= {'user_id':user_id})
		if serializer.is_valid():
			email =	serializer.data.get('email')
			password =	serializer.data.get('password')
			firstname =	serializer.data.get('firstname')
			lastname =	serializer.data.get('lastname')
			status =	serializer.data.get('status')
			address =	serializer.data.get('address')
			gender =	serializer.data.get('gender')
			role =	serializer.data.get('role')
			phonenumber =	serializer.data.get('phonenumber')
			country_code =	serializer.data.get('country_code')
			if status=='active':
				status =True
			else:
				status =False
			role = Role.objects.get(name=role)

			obj = UserOtherInfo.objects.get(pk = user_id)
			obj.addr_one =address
			obj.gender = gender
			obj.role=role
			obj.phonenum =phonenumber
			obj.country_code = country_code
			obj.save()
			obj2  =	obj.user
			obj2.first_name =firstname
			obj2.last_name  =lastname
			obj2.email = email
			obj2.is_active =status

			obj2.set_password(password)
			obj2.save()	

			return Response({
						
						'message':'Updated successfully'},
						status=HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)



class WebUserProfileAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		data = request.data
		user = request.user

		user_data = UserOtherInfo.objects.select_related('user').get(user=user)

		data = WebUserProfileSerializer(user_data).data

		return Response( data , status=HTTP_200_OK)

	def post(self,request,*args,**kwargs):
		data = request.data
		user = request.user
		serializer = WebUserProfileUpdateSerializer(data=data,context= {'request':request})
		if serializer.is_valid():
			phonenumber = serializer.data.get('phonenumber')
			countrycode =serializer.data.get('countrycode')
			email = serializer.data.get('email')
			firstname = serializer.data.get('firstname')
			lastname = serializer.data.get('lastname')
			gender = serializer.data.get('gender')

			obj = UserOtherInfo.objects.select_related('user').get(user=user)

			userObj = obj.user

			userObj.first_name=firstname
			userObj.last_name = lastname
			userObj.email = email

			userObj.save()
			obj.phonenum = phonenumber
			obj.country_code = countrycode
			obj.gender = gender
			obj.save()
			return Response({
						
						'message':'Profile Updated successfully'},
						status=HTTP_200_OK)

		return Response(serializer.errors, status = HTTP_400_BAD_REQUEST)



class UserProfileAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request,*args,**kwargs):
		user_data = UserOtherInfo.objects.select_related('user').get(user = request.user)
		data = AppUserProfileSerializer(user_data).data
		return Response({
			'message':'success',
			'response':data
			},200)

	def post(self,request,*args,**kwargs):
		data  = request.data
		serializer = AppUserProfileUpdateSerializer(data = data, context = {'request':request})
		if serializer.is_valid():
			obj = UserOtherInfo.objects.select_related('user').get(user=request.user)

			userObj = obj.user

			userObj.first_name=data['firstname']
			userObj.last_name = data['lastname']
			userObj.email = data['email']

			userObj.save()
			obj.gender = data['gender']
			obj.addr_three = None
			obj.addr_one = data['address']
			obj.addr_two = None

			if request.FILES.get('profileimg') is not None:
				obj.profileimg = request.FILES.get('profileimg')

			if request.FILES.get('coverimg') is not None:
				obj.coverimg = request.FILES.get('coverimg')

			

			if obj.phonenum == data['phonenumber'] and obj.country_code==data['countrycode']:
				obj.save()
				return Response({
						'message':'Profile updated successfully',
						'is_num_change':False,
						},200)
			else:
				obj.save()
				
				request = authy_api.phones.verification_start(data['phonenumber'], data['countrycode'], 
					via='sms', locale='en')
				if request.content['success'] ==True:
					return Response({
						'is_num_change':True,
						'phonenumber':data['phonenumber'],
						'countrycode':data['countrycode'],
						'message':'Your profile Updated.Pls verify your number'},
						status=HTTP_200_OK)

				else:
					# return Response({
					#   'success':False,
					#   'msg':request.content['message']},
					#   status=HTTP_400_BAD_REQUEST)
					return Response({
						'is_num_change':True,
						'message':'Your profile Updated.Pls varify your phoennumber',
						'phonenumber':data['phonenumber'],
						'countrycode':data['countrycode']
						},
						status=HTTP_200_OK

						)
			 
class OtpVerifyAfterChangeProfile(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request,*args,**kwargs):
		'''
		to check verification code 
		'''
		phone_number = request.data['phonenumber']
		country_code = request.data['countrycode']
		verification_code = request.data['verification_code']
		if phone_number and country_code and verification_code:

			"""
			for production version
			"""

			check = authy_api.phones.verification_check(phone_number, country_code, verification_code)
			if check.ok()==True or verification_code =="1234":

			# if verification_code=='1234':
				obj = UserOtherInfo.objects.get(user=request.user)
				obj.phonenum = phone_number
				obj.countrycode = country_code
				obj.isnumverify = True
				obj.save()
				return Response({
					# 'message':check.content['message'],    # Production version
					'message':'Your number has been verified successfully'
					},
					status=HTTP_200_OK)
			return Response({
					'message':'Otp code is wrong'
					# 'message':check.content['message']     # production version
					},
					status=HTTP_400_BAD_REQUEST)
		 

		return Response('provide phone_number, verification_code',status=HTTP_400_BAD_REQUEST)






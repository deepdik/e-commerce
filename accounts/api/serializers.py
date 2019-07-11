import re
from django.db.models import Q

from rest_framework.serializers import(
     ModelSerializer,
     EmailField, 
     CharField,
     ValidationError,
     SerializerMethodField,
     Serializer,
     ImageField
     )
from django.contrib.auth import get_user_model

from rest_framework_jwt.settings import api_settings
from accounts.models import UserOtherInfo

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from accounts.tokens import account_activation_token

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()

#reset password
from . password_reset_form import MyPasswordResetForm

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from rest_framework.exceptions import APIException
import random

class APIException400(APIException):
    status_code = 400

class UserDetailSerializer(ModelSerializer):
    name = SerializerMethodField()

    def get_name(self,instance):
        return instance.first_name +" "+ instance.last_name

    class Meta:
        model = User
        fields = ['name']


class UserCreateSerializer(ModelSerializer):
    token           = CharField(allow_blank=True, read_only=True)
    firstname       = CharField()
    lastname        = CharField() 
    email           = EmailField()
    phonenumber     = CharField()
    message         = CharField(allow_blank=True, read_only=True)                   
    success         = CharField(allow_blank=True, read_only=True)
    device_token    = CharField()
    device_type     = CharField()
    countrycode     = CharField()
    isnumverify     = CharField(allow_blank=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['firstname', 'lastname','email', 'password','isnumverify','message','success', 'phonenumber','countrycode','device_token', 'device_type', 'token']
        extra_kwargs = {'password': {'write_only': True}}


            
    def validate(self, data):
        phonenumber = data['phonenumber']
        password = data['password']
        device_token = data['device_token']
        device_type = data['device_type']
        countrycode = data['countrycode']
        email   = data['email']
        
        # number validation 

        if phonenumber.isdigit():
            user_qs = UserOtherInfo.objects.filter(phonenum__iexact=phonenumber,country_code=countrycode)
            if user_qs.exists():
                raise APIException400({
                'message':'User with this phonenumber already exists',
                'success':"false"
                })
            
        else:
            raise APIException400({
                'message':'Please correct your number',
                'success':"false"
                })

        # email validation

        # allowedDomains = [
        # "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
        # "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
        # "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
        # "email.com", "games.com" , "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
        # "lavabit.com", "love.com" , "outlook.com", "pobox.com", "rocketmail.com",
        # "safe-mail.net", "wow.com", "ygm.com" , "ymail.com", "zoho.com", "fastmail.fm",
        # "yandex.com","iname.com","fluper.in"
        # ]

        # domain = email.split("@")[1]
        # if domain not in allowedDomains:
        #     raise APIException400({
        #         'message':'Invalid Email address',
        #         'success':"false"
        #         })
        user_qs = User.objects.filter(email__iexact = email)
        if user_qs.exists():
            raise APIException400({
                'message':'User with this Email already exists',
                'success':"false"
                })
        

        # pass validation

        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters',
                'success':"false"
                })
        

        # device type validation

        if device_type not in ['ios','web','android']:
            
            raise APIException400({
                    'message':'Please enter correct format of device_type',
                    'success':"false"
                    })
        return data

    def create(self, validatedData):
        password = validatedData['password']
        firstname = validatedData['firstname']
        lastname = validatedData['lastname']
        phonenumber = validatedData['phonenumber']
        device_token = validatedData['device_token']
        device_type = validatedData['device_type']
        country_code = validatedData['countrycode']
        email  = validatedData['email']

        username =  firstname+lastname+str(random.randint(100000 ,10000000))     
        userObj = User(email=email, username=username, first_name=firstname,
            last_name=lastname
            )

        userObj.set_password(password)
        userObj.save() #

        UserOtherInfo.objects.create(user=userObj,country_code=country_code, phonenum = phonenumber,device_type=device_type,device_token=device_token)

        payload = jwt_payload_handler(userObj)
        token = jwt_encode_handler(payload)
        
        validatedData['token'] = token
        validatedData['success'] = "true"
        validatedData['isnumverify'] = "false"
        validatedData['message'] = 'Account created successfully.Please verify your phone number'
        return validatedData

class UserLoginSerializer(ModelSerializer):
    token = CharField(allow_blank=True, read_only=True)
    phonenumber = CharField()
    firstname = CharField(allow_blank=True, read_only=True)
    lastname = CharField(allow_blank=True, read_only=True)
    device_token = CharField()
    device_type  = CharField()
    countrycode     = CharField()
    isprofile_created  = CharField(allow_blank=True, read_only=True)
    isnumverify  = CharField(allow_blank=True, read_only=True)
    message      = CharField(allow_blank=True, read_only=True)                   
    success      = CharField(allow_blank=True, read_only=True)
    def validate(self, data):
        userObj = None
        phonenumber = data['phonenumber']
        password = data['password']
        device_token = data['device_token']
        device_type = data['device_type']
        countrycode = data['countrycode']

         
        # userA =User.objects.filter(username__iexact=phonenumber)
        # userB =User.objects.filter(email__iexact=phonenumber)
        # user = userA | userB
        # user = user.exclude(email__isnull=True).exclude(email__iexact='').distinct()
        # if user.exists() and user.count() == 1:           
        #   userObj = user.first()
        # else:
        #   raise ValidationError("Phone Number is not exist")

        userA =UserOtherInfo.objects.filter(phonenum=phonenumber,country_code=countrycode)
        user = userA.exclude(phonenum__isnull=True).exclude(phonenum__iexact='').distinct()
        if user.exists() and user.count() == 1:
            userObject = user.first()
        else:
            raise APIException400({
                'message':'Invalid credentials',
                'success':"false"
                })

        if userObject:
            # if not userObj.is_active:
            #   raise ValidationError("Please confirm your email")
            userObj = userObject.user
            passPasses = userObj.check_password(password)
            if passPasses:
                userObject.device_token = device_token
                userObject.device_type = device_type
                userObject.save()
                payload = jwt_payload_handler(userObj)
                token = jwt_encode_handler(payload)
                data['email'] = userObj.email
                data['token'] = token
                data['firstname'] = userObj.first_name
                data['lastname'] = userObj.last_name
                data['message'] = 'successfully login'
                data['success'] = "true"
                data['isprofile_created'] = (str(userObject.isprofile_created)).lower()
                data['isnumverify'] = (str(userObject.isnumverify)).lower()
                return data
        raise APIException400({
                'message':'Invalid credentials',
                'success':"false"
                })
    class Meta:
        model = User
        fields = ['message','success','isnumverify','countrycode','isprofile_created','token', 'phonenumber','password','firstname','lastname','device_token','device_type']

        extra_kwargs = {'password': {'write_only': True}}

class ChangePasswordSerializer(Serializer):
    oldPassword = CharField(required=True)
    newPassword = CharField(required=True)
    # confPassword = CharField(required=True)

    def validate_oldPassword(self, password):
        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters',
                'success':"false"
                })
        return password
    def validate_newPassword(self, password):
        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters',
                'success':"false"
                })
        return password
    # def validate_confPassword(self, password):
    #     if len(password) < 8:
    #         raise APIException400({
    #             'message':'Password must be at least 8 characters',
    #             'success':"false"
    #             })
    #     return password

class PasswordResetSerializer(serializers.Serializer):

    """
    Serializer for requesting a password reset e-mail.
    """

    email = serializers.EmailField()
    class Meta:
        model = User
        fields = [
           
            'email',                       
        ]

    password_reset_form_class = MyPasswordResetForm

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(_('Error'))

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('This e-mail address is not linked with any account'))

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }
        self.reset_form.save(**opts)


class OTPcreateSerializer(Serializer):
    email           = EmailField()
    phonenumber     = CharField()
    message             = CharField(allow_blank=True, read_only=True)                   
    success         = CharField(allow_blank=True, read_only=True)
    password        = CharField()

    def validate_phonenumber(self, phonenumber):
        
        if phonenumber.isdigit() and len(phonenumber) == 10:
            user_qs = UserOtherInfo.objects.filter(phonenum=phonenumber)
            if user_qs.exists():
                raise APIException400({
                'message':'User with this phonenumber already exists',
                'success':"false"
                })
                
            return phonenumber

        raise APIException400({
                'message':'Please correct your number',
                'success':"false"
                })


    def validate_email(self, email):
        # allowedDomains = [
        # "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
        # "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
        # "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
        # "email.com", "games.com" , "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
        # "lavabit.com", "love.com" , "outlook.com", "pobox.com", "rocketmail.com",
        # "safe-mail.net", "wow.com", "ygm.com" , "ymail.com", "zoho.com", "fastmail.fm",
        # "yandex.com","iname.com","fluper.in"
        # ]

        # domain = email.split("@")[1]
        # if domain not in allowedDomains:
        #     raise APIException400({
        #         'message':'Invalid Email address',
        #         'success':"false"
        #         })
        user_qs = User.objects.filter(email__iexact = email)
        if user_qs.exists():
            raise APIException400({
                'message':'User with this Email already exists',
                'success':"false"
                })
        return email

    def validate_password(self, password):
        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters long',
                'success':"false"
                })
        return password


class ResetPasswordByPhoneSerializer(Serializer):
    password = CharField(required=True)
    confpassword = CharField(required=True)

    def validate_password(self, password):
        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters long',
                'success':"false"
                })
        return password
    def validate_confpassword(self, password):
        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters long',
                'success':"false"
                })
        return password

class UserDeatilSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'is_active'
        ]



class AdminUserViewSerializer(ModelSerializer):
    userotherinfo = SerializerMethodField()


    def get_userotherinfo(self,instance):
       
        data  = UserDeatilSerializer(instance.user).data
        return data


    class Meta:
        model = UserOtherInfo
        fields = [
            'phonenum',
            'profileimg',
            'addr_one',
            'addr_two',
            'addr_three',
            'about',
            'gender',
            'userotherinfo'

        ]

class AdminUserListSerializer(ModelSerializer):
    userotherinfo = SerializerMethodField()



    def get_userotherinfo(self,instance):
        user = User.objects.get(pk = instance.user.id)
        data  = UserDeatilSerializer(user).data
        return data


    class Meta:
        model = UserOtherInfo
        fields = [
            'id',
            'phonenum',
            'profileimg',
            'region',
            'about',
            'device_type',
            'role',
            'rating',
            'gender',
            'region',
            'userotherinfo'

        ]



class AddNewMemberSerializer(Serializer):
    email           = CharField(error_messages={'required': "Give yourself a username",'invalid':"Please enter a valid email"})
    phonenumber     = CharField()
    country_code    = CharField()
    password        = CharField(allow_blank=False ,trim_whitespace=False)
    firstname       = CharField()
    lastname        = CharField()
    role            = CharField()
    gender          = CharField()
    status          = CharField()
    address         = CharField(allow_blank=True)


    def validate_email(self, email):
        # allowedDomains = [
        # "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
        # "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
        # "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
        # "email.com", "games.com" , "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
        # "lavabit.com", "love.com" , "outlook.com", "pobox.com", "rocketmail.com",
        # "safe-mail.net", "wow.com", "ygm.com" , "ymail.com", "zoho.com", "fastmail.fm",
        # "yandex.com","iname.com","fluper.in"
        # ]
        if email.count('@')>1:
            raise APIException400({
                'message':'Please enter a valid email',
                
                })
        try:

            domain = email.split("@")[1]
        except:
            raise APIException400({
                'message':'Please enter a valid email',
                
                })
        # if domain not in allowedDomains:
        #     raise APIException400({
        #         'message':'Please enter a valid email',
                
        #         }) 
        
        user_qs = User.objects.filter(email__iexact = email)
        if user_qs.exists():
            raise APIException400({
                    'message':'User with this Email already exists',
                    'email_error':True,
                    'phone_error':False,
                    'pass_error':False
                    
                    })
        return email

    # def validate_country_code(self,country_code):
        
    #     if country_code.isdigit():
    #         return country_code
    #     raise APIException400({
    #                 'message':'Country code should be in digit',
    #                 'email_error':False,
    #                 'phone_error':True,
    #                 'pass_error':False
    #                 })

    def validate_phonenumber(self, phonenumber):

        if phonenumber.isdigit() and len(phonenumber) <12:

            user_qs = UserOtherInfo.objects.filter(phonenum__iexact=phonenumber)
            if user_qs.exists():
                    raise APIException400({
                    'message':'User with this phonenumber already exists',
                    'email_error':False,
                    'phone_error':True,
                    'pass_error':False
                    })
                
            return phonenumber
        raise APIException400({
                'message':'Please enter a valid Mobile Number',
                'email_error':False,
                'phone_error':False,
                'pass_error':True
                
                })

    def validate_password(self, password):
        if password == '':
            raise APIException400({
                'message':'Please enter a valid password',
                'email_error':False,
                'phone_error':False,
                'pass_error':True
                
                })

        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters long',
                'email_error':False,
                'phone_error':False,
                'pass_error':True
                
                })


        return password


class EditNewMemberSerializer(Serializer):
    email           = CharField()
    phonenumber     = CharField()
    country_code    = CharField()
    password        = CharField(allow_blank=False ,trim_whitespace=False)
    firstname       = CharField()
    lastname        = CharField()
    role            = CharField()
    gender          = CharField()
    status          = CharField()
    address         = CharField(allow_blank=True,)


    def validate_email(self, email):

        user_id = self.context['user_id']
        obj = UserOtherInfo.objects.select_related('user').get(pk =user_id)
        if not obj.user.email == email: 
            print(user_id)
            # allowedDomains = [
            # "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
            # "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
            # "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
            # "email.com", "games.com" , "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
            # "lavabit.com", "love.com" , "outlook.com", "pobox.com", "rocketmail.com",
            # "safe-mail.net", "wow.com", "ygm.com" , "ymail.com", "zoho.com", "fastmail.fm",
            # "yandex.com","iname.com","fluper.in"
            # ]
            if email.count('@')>1:
                raise APIException400({
                'message':'Please enter a valid email',
                
                })
            try:
                domain = email.split("@")[1]
            except:
                raise APIException400({
                    'message':'Please enter a valid email',
                    
                    })

            # if domain not in allowedDomains:
            #     raise APIException400({
            #         'message':'Please enter a valid email',
                    
            #         })
            
            user_qs = User.objects.filter(email__iexact = email)
            if user_qs.exists():
                raise APIException400({
                    'message':'User with this Email already exists',
                    'email_error':True,
                    'phone_error':False,
                    'pass_error':False
                    
                    })
            return email

        return email

    # def validate_country_code(self,country_code):

    #     if country_code.isdigit():
    #         return country_code
    #     raise APIException400({
    #                 'message':'Country code should be in digit',
    #                 'email_error':False,
    #                 'phone_error':True,
    #                 'pass_error':False
    #                 })


    def validate_phonenumber(self, phonenumber):

        if phonenumber.isdigit() and len(phonenumber)>12:
            user_id = self.context['user_id']
            obj = UserOtherInfo.objects.get(pk =user_id)
            if not obj.phonenum==phonenumber:
                user_qs = UserOtherInfo.objects.filter(phonenum__iexact=phonenumber)
                if user_qs.exists():
                    raise APIException400({
                    'message':'User with this phonenumber already exists',
                    'email_error':False,
                    'phone_error':True,
                    'pass_error':False
                    })
                return phonenumber
            return phonenumber
        raise APIException400({
                'message':'Please correct your number',
                'email_error':False,
                'phone_error':False,
                'pass_error':True
                
                })

    def validate_password(self, password):
        if password == '':
            raise APIException400({
                'message':'Please enter a valid password',
                'email_error':False,
                'phone_error':False,
                'pass_error':True
                
                })
        if len(password) < 8:
            raise APIException400({
                'message':'Password must be at least 8 characters long',
                'email_error':False,
                'phone_error':False,
                'pass_error':True
                
                })

        return password


class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        fields = [
            'email',
            'first_name',
            'last_name',

        ]



class WebUserProfileSerializer(ModelSerializer):
    user_other_data = SerializerMethodField()

    def get_user_other_data(self,instance):
        return UserSerializer(instance.user).data


    class Meta:
        model = UserOtherInfo
        fields =[
            'phonenum',
            'country_code',
            'gender',
            'user_other_data'

        ]

class WebUserProfileUpdateSerializer(Serializer):

    email           = CharField()
    phonenumber     = CharField()
    countrycode     = CharField()
    firstname       = CharField()
    lastname        = CharField()
    gender          = CharField(required=False, allow_null=True)

    def validate_email(self, email):

        request = self.context['request']
        user = request.user
        obj = UserOtherInfo.objects.select_related('user').get(user=user)
        if not obj.user.email == email: 
            # allowedDomains = [
            # "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
            # "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
            # "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
            # "email.com", "games.com" , "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
            # "lavabit.com", "love.com" , "outlook.com", "pobox.com", "rocketmail.com",
            # "safe-mail.net", "wow.com", "ygm.com" , "ymail.com", "zoho.com", "fastmail.fm",
            # "yandex.com","iname.com","fluper.in"
            # ]
            if email.count('@')>1:
                raise APIException400({
                'message':'Please enter a valid email',
                
                })
            try:
                domain = email.split("@")[1]
            except:
                raise APIException400({
                    'message':'Please enter a valid email',
                    
                    })

            # if domain not in allowedDomains:
            #     raise APIException400({
            #         'message':'Please enter a valid email',
                    
            #         })
            
            user_qs = User.objects.filter(email__iexact = email)
            if user_qs.exists():
                raise APIException400({
                    'message':'User with this Email already exists',
                    'email_error':True,
                    'phone_error':False,
                    'pass_error':False
                    
                    })
            return email

        return email

    def validate_phonenumber(self, phonenumber):
        if phonenumber.isdigit():
            user = self.context['request'].user
            obj = UserOtherInfo.objects.get(user =user)
            if not obj.phonenum == phonenumber:
                user_qs = UserOtherInfo.objects.filter(phonenum__iexact=phonenumber)
                if user_qs.exists():
                    raise APIException400({
                    'message':'User with this phonenumber already exists',
                    'email_error':False,
                    'phone_error':True,
                    'pass_error':False
                    })
                return phonenumber
            return phonenumber
        raise APIException400({
                'message':'Please correct your number',
                'email_error':False,
                'phone_error':False,
                'pass_error':True
                
                })


class AppUserProfileSerializer(ModelSerializer):
    email = SerializerMethodField()
    first_name  = SerializerMethodField()
    last_name  = SerializerMethodField()
    address  = SerializerMethodField()

    def get_first_name(self,instance):
        return instance.user.first_name
    def get_last_name(self,instance):
        return instance.user.last_name
    def get_email(self,instance):
        return instance.user.email

    def get_address(self,instance):
        addr_1 = instance.addr_one
        addr_2 = instance.addr_two
        addr_3 = instance.addr_three

        if addr_1 is None:
            addr_1 = ''
        if addr_2 is None:
            addr_2 = ''
        if addr_3 is None:
            addr_3 = ''
        return addr_1 + ' ' + addr_2 + ' ' + addr_3

        
    class Meta:
        model = UserOtherInfo
        fields =[
            'phonenum',
            'country_code',
            'isnumverify',
            'email',
            'first_name',
            'last_name',
            'gender',
            'profileimg',
            'coverimg',
            'address',

        ]

class AppUserProfileUpdateSerializer(Serializer):

    email           = CharField()
    phonenumber     = CharField()
    countrycode     = CharField()
    firstname       = CharField()
    lastname        = CharField()
    gender          = CharField()
    address         = CharField()

    def validate_email(self, email):

        request = self.context['request']
        user = request.user
        obj = UserOtherInfo.objects.select_related('user').get(user=user)
        if not obj.user.email == email: 
            # allowedDomains = [
            # "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
            # "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
            # "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
            # "email.com", "games.com" , "gmx.net", "hush.com", "hushmail.com", "icloud.com", "inbox.com",
            # "lavabit.com", "love.com" , "outlook.com", "pobox.com", "rocketmail.com",
            # "safe-mail.net", "wow.com", "ygm.com" , "ymail.com", "zoho.com", "fastmail.fm",
            # "yandex.com","iname.com","fluper.in"
            # ]
            if email.count('@')>1:
                raise APIException400({
                'message':'Please enter a valid email',
                
                })
            try:
                domain = email.split("@")[1]
            except:
                raise APIException400({
                    'message':'Please enter a valid email',
                    
                    })

            # if domain not in allowedDomains:
            #     raise APIException400({
            #         'message':'Please enter a valid email',
                    
            #         })
            
            user_qs = User.objects.filter(email__iexact = email)
            if user_qs.exists():
                raise APIException400({
                    'message':'User with this Email already exists',

                    })
            return email

        return email

    def validate_phonenumber(self, phonenumber):
        if phonenumber.isdigit():
            user = self.context['request'].user
            obj = UserOtherInfo.objects.get(user =user)
            if not obj.phonenum == phonenumber:
                user_qs = UserOtherInfo.objects.filter(phonenum__iexact=phonenumber)
                if user_qs.exists():
                    raise APIException400({
                    'message':'User with this phonenumber already exists',

                    })
                return phonenumber
            return phonenumber
        raise APIException400({
                'message':'Please enter a valid phonenumber',
                
                })

from django.urls import path

from .views import *

urlpatterns = [
	# path('register/',UserCreateAPIView.as_view(),name="register"),
	path('login/',UserLoginAPIView.as_view(),name="login"),
	path('changepassword/',ChangePasswordAPIView.as_view(),name="changePassword"),
	path('password/reset/', PasswordResetView.as_view(),
    name='rest_password_reset'),

    path('profile/create/', ProfileCreateAPIView.as_view(),
    name='profile_create'),

    path('webuser/profile', WebUserProfileAPIView.as_view(),
    name='web_profile_create'),


    path('register/otp/generate/', OTPCreateForRegistrationAPIView.as_view(),name="OtpVarifyAPIView"), # durring resgitration
    path('otp/verify/', UserPhoneVerifyAfterRegisterAPIView.as_view(),name="register"),
    path('otp/regenerate/', OTPSendForPhoneVerify.as_view(),name="register"),

    # pass re-set by phone production
    path('otp/generate/password/reset/',OtpGenerateForPasswordResetAPIView.as_view(),name="pass-reset-otp"),
    path('otp/verify/password/reset/',OtpVarifyForPasswordResetAPIView.as_view(),name="pass-reset-otp"),
    path('password/reset/byotp/',PasswordResetByPhoneAPIView.as_view(),name="pass-reset-otp"),


    # path('otp/generate/reset/',PasswordResetByPhoneAPIView.as_view(),name="pass-reset-otp"),
    # path('otp/generate/verify/',PasswordResetVerifyAPIView.as_view(),name="pass-reset-otp"),

    path('list/<int:user_id>',AdminUserViewAPIView.as_view(),name="admin-user-api"),
    path('block/<int:user_id>',AdminUserBlockAPIView.as_view(),name="admin-user-block-api"),
    path('unblock/<int:user_id>',AdminUserUnblockAPIView.as_view(),name="admin-user-unblock-api"),
    path('delete/<int:user_id>',AdminUserDeleteAPIView.as_view(),name="admin-user-delete-api"),
    path('edit/<int:user_id>',EditMemberAPIView.as_view(),name="admin-user-edit-api"),


# user filter 

    path('filter/<int:profile_id>',AdminUsersFilterAPIView.as_view(),name="admin-user-filter-api"),

# add new members

    path('addnew',AddNewMemberAPIView.as_view(),name="admin-addnewuser-api"),


# app user profile

    path('user_profile',UserProfileAPIView.as_view(),name="app-user-profile"),
    path('number_verify',OtpVerifyAfterChangeProfile.as_view(),name="app-user-num-verify"),


]
from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.conf.urls import url,include

urlpatterns = [
    path('login/', AdminLoginView.as_view(),name='admin-login'),
    path('home/', AdminHomeView.as_view(),name='admin-home'),
    path('logout/',LogoutView.as_view(),name='admin-logout'),

# password reset by mail
    url(r'^password_reset/$', ResetPasswordView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView, name='password_reset_complete'),

# change password
	path('change_password/',login_required(ChangePasswordView.as_view()),name='admin-change-password'),

# admin-profile

	path('admin_profile/',login_required(AdminProfileView.as_view()),name='admin-profile'),
	path('admin_profile/edit',login_required(AdminProfileEditView.as_view()),name='admin-profile-edit'),

# members-management

	path('member/',login_required(AdminMemberView.as_view()),name='admin-member'),

# user-management

	path('user_list/',login_required(AdminUserListView.as_view()),name='admin-user-list'),

# stylist-management
	path('stylist_list/',login_required(AdminStylistListView.as_view()),name='admin-designer-list'),


# designer-management
	path('designer_list/',login_required(AdminDesignerListView.as_view()),name='admin-stylist-list'),


# manufacturer-management
	path('manufacturer_list/',login_required(AdminManufacturerListView.as_view()),name='admin-manufacturer-list'),


# add new member

	path('add_member/<int:role>',login_required(addNewUserView.as_view()),name='admin-addmanufacturer-list'),
	path('edit_member/<int:role>/<int:profile_id>',login_required(EditNewUserView.as_view()),name='edit-admin-addmanufacturer-list'),

#date filter

	path('date_filter/<int:role>',login_required(MemberDateFilterView.as_view()),name='admin-manufacturer-filter-list'),

# user detail 

	path('user_detail/<int:profile_id>',login_required(UserdetailView.as_view()),name='admin-user-detail'),


# member detail 

	path('member_detail/<int:profile_id>',login_required(MemberdetailView.as_view()),name='admin-member-detail'),


# app in profile 


	path('appin_profile/<int:role>',login_required(AppInProfileCreateView.as_view()),name='app-in-profile-create'),
	path('appin_profile/<int:role>/<int:profile_id>',login_required(AppInProfileEditView.as_view()),name='app-in-profile-edit'),

	path('collection/',login_required(StylistDesignerCollectionView.as_view()),name='collection'),
	path('section_create/',login_required(StylistDesignerSectionCreateView.as_view()),name='section-edit'),
	path('section_edit/<int:section_id>',login_required(StylistDesignerSectionEditView.as_view()),name='section-edit'),
	path('section_select_product/<int:section_id>',login_required(StylistDesignerSelectExistingProduct.as_view()),name='section-select-product'),

# stylist designer product management

	path('product_list/',login_required(StylistDesignerProductList.as_view()),name='section-select-product'),

	path('add_category/',login_required(StylistDesignerCategory.as_view()),name='add-category'),
	
	path('add_product/',login_required(StylistDesignerAddProduct.as_view()),name='add-product'),

	path('add_product_varients/<int:product_id>',login_required(StylistDesignerAddProductVarientsView.as_view()),name='add-product-varients'),

	path('view_product/<int:product_id>',login_required(StylistDesignerViewProductView.as_view()),name='view-product'),

	path('view_product_varients/<int:product_id>',login_required(StylistDesignerViewProductVarientsView.as_view()),name='view-product-varients'),

	path('product_date_filter/<int:role>',login_required(StylistDesignerProductDatefilter.as_view()),name='product_date_filter'),

	path('edit_product/<int:product_id>',login_required(StylistDesignerProductEditView.as_view()),name='edit-product'),
	
	path('edit_product_varient/<int:product_id>/<int:varient_id>',login_required(StylistDesignerProductVarientEditView.as_view()),name='edit-product-varient'),

	path('search_product',login_required(ProductSearchByCatSubAndSubSubView.as_view()),name='search-product'),


# admin offer mamagement

	path('coupon_management/',login_required(CouponView.as_view()),name='coupon'),
	path('coupon_add/',login_required(AddCouponView.as_view()),name='coupon_add'),

	path('coupon_edit/<int:coupon_id>',login_required(EditCouponView.as_view()),name='coupon_edit'),


# delivery management 

	path('delivery_charges/',login_required(DeliveryChargesView.as_view()),name='delivery_charges'),
	path('delivery_charges_edit/',login_required(EditDeliveryCharges.as_view()),name='charges_edit'),
	

# refund and return policy

	path('return_and_refund_policy/',login_required(ReturnAndRefundPolicy.as_view()),name='return_and_refund_policy'),

# settings management

	path('terms_about_contact/',login_required(TermsAboutContactView.as_view()),name='terms_about_contact'),
	path('faq/',login_required(FAQView.as_view()),name='faq'),

# order management

	path('order/',login_required(OrderView.as_view()),name='faq'),



]




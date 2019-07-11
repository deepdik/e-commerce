from django.urls import path

from .views import *

urlpatterns = [

	path('delete_appin_img/<int:image_id>',DeleteAppInAchievementImgAPIView.as_view(),name="delete_appin_img"),
	path('section/delete/<int:section_id>',StylistDesignerSectionDeleteAPIView.as_view(),name="delete_section"),
	path('section/product/remove/<int:product_id>',StylistDesignerProductRemoveAPIView.as_view(),name="section_product_remove"),
	path('section/product/add/<int:section_id>',StylistDesignerProductAddAPIView.as_view(),name="section_product_add"),

# product stylist designer

	path('designer_stylist/product/delete/<int:product_id>',StylistDesignerProductDeleteAPIView.as_view(),name="product_delete"),
	path('designer_stylist/category/<int:category_id>',StylistDesignerCategoryAPIView.as_view(),name="category"),
	path('designer_stylist/product/status_change/<int:product_id>/<str:status>',StylistDesignerProductActiveInactiveAPIView.as_view(),name="product_status_change"),
	path('designer_stylist/product/image/delete/<int:image_id>',StylistDesignerProductImageDeleteAPIView.as_view(),name="product_image_delete"),
	path('designer_stylist/product/colour/delete/<int:colour_id>',StylistDesignerProductColourDeleteAPIView.as_view(),name="product_colour_delete"),

	path('designer_stylist/product/colour/image/delete/<int:image_id>',StylistDesignerProductColourImageDeleteAPIView.as_view(),name="product_image_delete"),
	path('designer_stylist/product/varient/delete/<int:product_id>/<int:varient_id>',StylistDesignerProductVarientDeleteAPIView.as_view(),name="product_delete"),

# admin coupon management

	path('coupon/<int:coupon_id>',CouponAPIView.as_view(),name="coupon_delete"),
	path('coupon_status/<int:coupon_id>/<str:status>',CouponStatusChangeAPIView.as_view(),name="coupon_status_change"),

# delivery charge

	path('delivery_charge/<int:deliveryCharge_id>',DeliveryChagresDeleteAPIView.as_view(),name="delivery_charge_delete"),

# faq delete

	path('delete_faq/<int:faq_id>',FAQDeleteAPIView.as_view(),name="faq_delete"),





]
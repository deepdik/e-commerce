from django.urls import path

from .views import *

urlpatterns = [
	path('list/designer',DesignerListAPIView.as_view(),name="designer-list"),
   path('list/designer/<int:designer_id>',DesignerDetailAPIView.as_view(),name="designer-list"),
	path('list/stylist',StylistListAPIView.as_view(),name="stylist-list"),
	path('list/stylist/<int:stylist_id>',StylistDetailAPIView.as_view(),name="stylist-list"),
	path('list/product/<int:profile_id>',ProductListAPIView.as_view(),name="product-list"),
	# path('list/product/<int:profile_id>',ProductListAPIView.as_view(),name="product-list"),
	path('filter/product/<int:profile_id>',StylistDesignerProductFilterList.as_view(),name="product-list"),
	

	# for web 

	path('list/product/web/<int:profile_id>',StylistDesignerProductListWebView.as_view(),name="web-product-list"),

	path('detail/product/<int:profile_id>/<int:product_id>/',ProductDetailAPIView.as_view(),name="product-detail"),
   path('detail/product/bycolur/<int:profile_id>/<int:product_id>/<int:colour_id>',ProductDetailByColourAPIView.as_view(),name="product-detail"),

 # end web


]














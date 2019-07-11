from django.urls import path

from .views import *

urlpatterns = [
	path('category/',CategoryListAPIView.as_view(),name="category"),
    path('subcategory/<int:cat_id>/',SubCategoryListAPIView.as_view(),name="subcategory"),
    path('subsubcategory/<int:cat_id>/<int:subcat_id>/',SubSubCategoryListAPIView.as_view(),name="sub-subcategory"),
    path('<int:cat_id>/<int:subcat_id>/<int:subsubcat_id>/',ProductListAPIView.as_view(),name="sub-subcategory"),
    path('detail/<int:product_id>/',ProductDetailAPIView.as_view(),name="sub-subcategory"),

    path('detail_by_colour/<int:product_id>/<int:id>',GetDetailOfProductByColourAPIView.as_view(),name="sub-subcategory"),

    path('web/detail/<int:product_id>/',ManufacturerProductDetailAPIView.as_view(),name="web-product-detail"),
    path('web/view/detail/<int:product_id>/',ProductDetailForWebViewAPIView.as_view(),name="web-product-view-detail"),
    path('web/detail/by_colour/<int:product_id>/<int:colour_id>',ManufacturerProductDetailByColourAPIView.as_view(),name="mf-product-detail-by-colour"),

    path('search',SearchProducts.as_view(),name="search-product"),
    path('search_web',SearchProductsWeb.as_view(),name="search-product-web"),

    path('subcategory/',SubCategoryListAPIView.as_view(),name="subcategory"),
    path('sub-subcategory/',SubSubCategoryListAPIView.as_view(),name="sub-subcategory"),
    path('home_page',HomePage.as_view(),name="home_page"),
    path('web_home_page',WebHomePage.as_view(),name="web_home_page"),

    path('wishlist/',WishListAPIView.as_view(),name="wishlist"),
    path('wishlist/<int:product_id>',DeleteFromWishlistAPIView.as_view(),name="delete_wishlist"),

    path('cart/',CartListAPIView.as_view(),name="cart"),
    path('cart/<int:cart_id>',DeleteFromCartAPIView.as_view(),name="cart-delete"),

    path('change_cart_qty/',ChangeCartItems.as_view(),name="cart2"),

    path('coupon_apply/',CouponApplyCheckingAPIView.as_view(),name="coupon_apply"),
    path('coupon_remove/',RemoveCouponAPIView.as_view(),name="coupon_remove"),

]







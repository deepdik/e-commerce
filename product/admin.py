from django.contrib import admin
from .models import *
# Register your models here.



class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductImageInline,)



class ProductFilterSubTagInline(admin.StackedInline):
    model = ProductFilterSubTag


class ProductFilterTagAdmin(admin.ModelAdmin):
    inlines = (ProductFilterSubTagInline,)

admin.site.register(ProductFilterTag,ProductFilterTagAdmin)

admin.site.register(Product,ProductAdmin)

admin.site.register([Category,ProductImageByColour,ProductAvailableColourWithSizeQty,ProductSizeWithQty,CoupanCodeUseLimit,DeliveryDistanceManagement, CustomerProductWishList,CouponCode,CustomerProductCart,ProductImage, ProductAvailableAllColour, HomePageImage,SubCategory,SubSubCategory,Size,Colour,ProductReviews])


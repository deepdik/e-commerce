from django.urls import path

from .views import *

urlpatterns = [

	path('deliver_address' ,DeliveryAddressAPIView.as_view(), name="add_getall_address"),
	path('deliver_address/<int:addr_id>' ,ActionOnDeliveryAddressAPIView.as_view(), name="edit_delete_address"),

	path('places_order' ,MakeOrderAPIView.as_view(), name="place_order"),

	# path('orders_history' ,OrderHistoryAPIView.as_view(), name="orders_history"),

	path('orders_history' ,AllOrderProductHistoryAPIView.as_view(), name="orders_history"),
	path('orders_history/<int:id>' ,OrderedProductHistoryAPIView.as_view(), name="ordered_product_history"),

]





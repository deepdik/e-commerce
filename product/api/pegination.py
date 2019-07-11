from rest_framework.pagination import PageNumberPagination

class ShortPaginator(PageNumberPagination):
	page_size = 1
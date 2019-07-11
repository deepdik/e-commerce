from rest_framework import permissions
from rest_framework.response import Response



class IsAuthenticatedOrCreate(permissions.IsAuthenticated):
	def has_permission(self, request, view):
		if request.method == 'POST':
			return True
		return super(IsAuthenticatedOrCreate, self).has_permission(request, view)
		



class IsStaffUser(permissions.BasePermission):
   
	def has_permission(self, request, view):
		
		user = self.request.user

		# check user login

		if not user.is_authenticated:
			return Response({
				'message':'user is not authenticated'
				})

		return True


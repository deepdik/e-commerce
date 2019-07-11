from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
from django.conf import settings

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class HomePageView(TemplateView):
	template_name = 'payment.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['key'] = settings.STRIPE_PUBLISHABLE_KEY
		return context

def charge(request): # new
	if request.method == 'POST':

		print(request.POST)
		# charge = stripe.Charge.create(
		# 	amount=500,
		# 	currency='usd',
		# 	description='A Django charge',
		# 	customer = 'cus_F1U7LNSFUNdDrB',
		# 	source=request.POST['stripeToken']
		# )
		return render(request, 'charge.html')





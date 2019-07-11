"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url,include
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import activate


from payments.views import HomePageView, charge

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/users/',include(('admin_panel.urls','admin_panel'),namespace="admin-panel")),

    path('api/v1/users/',include(('accounts.api.urls','accounts'),namespace="users-api")),
    path('api/v1/order/',include(('orders.api.urls','orders'),namespace="orders-api")),

    path('api/v1/payment/',include(('payments.api.urls','payemnts'),namespace="payments-api")),

    url(r'^api/v1/product/',include(('product.api.urls','product'),namespace="product-api")),
    url(r'^api/v1/admin/',include(('admin_panel.api.urls','admin_panel'),namespace="admin-api")),
    url(r'^api/v1/profile/',include(('designer_stylist.api.urls','designer_stylist'),namespace="designer_stylist-api")),

    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',activate, name='activate'),#Email Activation
    url('^', include('django.contrib.auth.urls')),  # email varification
    path('', HomePageView.as_view(), name='home'),  # payment check
    path('charge/', charge, name='charge'),  # payment check

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
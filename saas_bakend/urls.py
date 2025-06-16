from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from saas.views import *
router=DefaultRouter()

router.register(r'clients', ClientViewSet),
router.register(r'users', UserViewSet),
router.register(r'leads', LeadViewSet),
router.register(r'plans', PlanViewSet),
router.register(r'subscription', SubscriptionViewSet)
router.register(r'roles',RoleViewSet)
router.register(r'permissions',PermissionViewSet)
urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),



    #router login URLs
    path('api-auth/', include('rest_framework.urls')),

    #Djoser URLs
    path('auth/', include('djoser.urls')),            # user management
    path('auth/', include('djoser.urls.jwt')),        # JWT endpoints



    path('', include(router.urls)),
]

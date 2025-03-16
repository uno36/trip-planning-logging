from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, calculate_route

router = DefaultRouter()
router.register(r'trips', TripViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('calculate_route/', calculate_route),
]

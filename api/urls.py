from django.urls import path

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from api.views import StudentProfileViewSet


app_name = 'api'
router = DefaultRouter()
urlpatterns = [
    path('get_auth_token/', obtain_auth_token),
]

router.register(r'users', StudentProfileViewSet, basename='users')
urlpatterns += router.urls
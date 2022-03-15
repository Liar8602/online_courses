from rest_framework.routers import DefaultRouter
from api.views import StudentProfileViewSet


app_name = 'api'
router = DefaultRouter()
urlpatterns = []

router.register(r'users', StudentProfileViewSet, basename='users')
urlpatterns += router.urls
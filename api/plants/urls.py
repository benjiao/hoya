from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, PlantViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'plants', PlantViewSet, basename='plant')

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter
from .views import LocationViewSet, PlantViewSet, PlantStatusViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'plants', PlantViewSet, basename='plant')
router.register(r'plant-statuses', PlantStatusViewSet, basename='plant-status')

urlpatterns = router.urls

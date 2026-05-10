from rest_framework.routers import DefaultRouter
from .views import JournalViewSet

router = DefaultRouter()

router.register(r'journals', JournalViewSet, basename='journals')

urlpatterns = router.urls
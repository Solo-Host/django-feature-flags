from rest_framework.routers import DefaultRouter

from feature_flags.views import FeatureFlagViewSet

app_name = "feature_flags"

router = DefaultRouter()
router.register("", FeatureFlagViewSet, basename="feature-flag")
urlpatterns = router.urls

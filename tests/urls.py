from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/feature-flags/",
        include(("feature_flags.urls", "feature_flags"), namespace="feature_flags"),
    ),
]

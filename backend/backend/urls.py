"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from common.views import PlantViewSet, ShamrockViewSet, ProfileViewSet, SnapShotViewSet, DeviceViewSet
router = routers.DefaultRouter()
router.register(r'plant', PlantViewSet)
router.register(r'shamrock', ShamrockViewSet, "shamrock")
router.register(r'profile', ProfileViewSet)
router.register(r'device', DeviceViewSet)
router.register(r'snapshot', SnapShotViewSet)

urlpatterns = [
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

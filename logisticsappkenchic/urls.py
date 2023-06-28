"""registrationform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pages.views import register_page, login_page, home_page, logout_user, admin2, login_admin, workerror, serve_apk, pending, upload_file
from pages.views import GenerateReportView
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['url', 'username', 'email', 'is_staff']

# # Serializers define the API representation.
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['url', 'username', 'email', 'is_staff']

# # ViewSets define the view behavior.
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
    # serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apis.urls')),
    path('router/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('register/', register_page, name="register"),
    path('login/', login_page, name="login"),
    path('logout/', logout_user, name="logout"),
    path('', home_page, name="home"),
    path('loginadmin/', login_admin, name="login_admin"),
    path('admin2/', admin2, name="admin2"),
    path('workerror/', workerror, name="workerror"),
    path('report/', GenerateReportView.as_view(), name="report"),
    path('apk/<str:filename>/', serve_apk, name='serve_apk'),
    path('pending/', pending, name='pending'),
    path('upload_file/', upload_file, name='upload_file'),



    # path('showform/', showform, name="showform"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

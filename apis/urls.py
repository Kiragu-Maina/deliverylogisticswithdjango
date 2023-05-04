from django.urls import path

from . import views
# from apis.views import HomePage

urlpatterns = [
    path('homeapigetroutes/', views.getRoutes),
    path('homeapi/',views.home_page),
    path('homeapi/login/', views.login_page),
    path('homeapi/csrf/', views.getcsrftoken),
    path('homeapi/submitform/', views.submit_form),
    path('homeapi/submitform2/', views.submit2_form),
    path('homeapi/trackingform/', views.tracking),
]

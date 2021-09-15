from django.urls import path

from . import views

app_name = "public"
urlpatterns = [
    path('', views.HomePage.as_view(), name='home_page'),
    path('about', views.AboutPage.as_view(), name='about_page'),
]


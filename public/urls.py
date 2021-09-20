from django.urls import path

from . import views

app_name = "public"
urlpatterns = [
    path('', views.HomePage.as_view(), name='home_page'),
    path('issues/<int:pk>', views.ShowIssue.as_view(), name='show_issue'),
    path('about', views.AboutPage.as_view(), name='about_page'),
]


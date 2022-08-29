from django.urls import path
from roles import views

app_name = "roles"
urlpatterns = [
    path('edit', views.EditProfile.as_view(), name="edit"),
    path('password', views.ChangePassword.as_view(), name="password"),
    path('', views.ShowProfile.as_view(), name="detail"),
]


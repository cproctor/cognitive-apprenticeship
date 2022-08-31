from django.urls import path

from . import views

app_name = "common"
urlpatterns = [
    path('email/<int:index>', views.TestEmail.as_view(), name='test_email'),
]


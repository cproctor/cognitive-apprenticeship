from django.urls import path

from . import views

urlpatterns = [
    path('', views.ReviewerHome.as_view(), name='reviewer_home'),
    path('manuscripts/<int:pk>', views.ReviewManuscript.as_view(), name='review_manuscript'),
]

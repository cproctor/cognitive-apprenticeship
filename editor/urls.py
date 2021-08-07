from django.urls import path

from . import views

urlpatterns = [
    path('', views.EditorHome.as_view(), name='editor_home'),
    path('manuscripts', views.ListEditorManuscripts.as_view(), name='list_editor_manuscripts'),
    path('reviews', views.ListEditorReviews.as_view(), name='list_editor_reviews'),
]


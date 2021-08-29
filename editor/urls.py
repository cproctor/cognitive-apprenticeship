from django.urls import path

from . import views

app_name = "editor"
urlpatterns = [
    path('', views.EditorHome.as_view(), name='home'),
    path('manuscripts', views.ListEditorManuscripts.as_view(), name='list_manuscripts'),
    path('manuscripts/<int:pk>', views.ShowEditorManuscript.as_view(), name='show_manuscript'),
    path('reviews', views.ListEditorReviews.as_view(), name='list_reviews'),
]


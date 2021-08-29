from django.urls import path

from . import views

app_name = "reviewer"
urlpatterns = [
    path('', views.ReviewerHome.as_view(), name='home'),
    path('manuscripts/<int:pk>', views.ShowManuscript.as_view(), name='show_manuscript'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>', 
            views.ShowRevision.as_view(), name='show_revision'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>/review', 
            views.ReviewRevision.as_view(), name='review_revision'),
]

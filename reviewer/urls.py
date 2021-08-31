from django.urls import path

from . import views

app_name = "reviewer"
urlpatterns = [
    path('', views.ReviewerHome.as_view(), name='home'),
    path('manuscripts/<int:pk>', views.ShowManuscript.as_view(), name='show_manuscript'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>', 
            views.ShowRevision.as_view(), name='show_revision'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>/reviews', 
            views.ShowReviews.as_view(), name='show_reviews'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>/review', 
            views.ShowReview.as_view(), name='show_review'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>/review/edit', 
            views.EditReview.as_view(), name='edit_review'),
]

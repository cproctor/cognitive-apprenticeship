from django.urls import path

from . import views

app_name = "author"
urlpatterns = [
    path('', views.AuthorHome.as_view(), name='home'),
    path('instructions', views.AuthorInstructions.as_view(), name='instructions'),
    path('manuscripts/new', views.NewManuscript.as_view(), name='new_manuscript'),
    path('manuscripts/<int:pk>', views.ShowManuscript.as_view(), name='show_manuscript'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>', 
            views.ShowRevision.as_view(), name='show_revision'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>/reviews', 
            views.ShowRevisionReviews.as_view(), name='show_revision_reviews'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>/edit', 
            views.EditRevision.as_view(), name='edit_revision'),
]

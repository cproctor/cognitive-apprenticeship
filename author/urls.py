from django.urls import path

from . import views

urlpatterns = [
    path('', views.AuthorHome.as_view(), name='author_home'),
    path('manuscripts/new', views.NewManuscript.as_view(), name='new_manuscript'),
    path('manuscripts/<int:pk>', views.ShowManuscript.as_view(), name='show_manuscript'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>', 
            views.ShowRevision.as_view(), name='show_revision'),
]

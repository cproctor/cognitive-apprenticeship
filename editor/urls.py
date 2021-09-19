from django.urls import path

from . import views

app_name = "editor"
urlpatterns = [
    path('', views.EditorHome.as_view(), name='home'),
    path('manuscripts', views.ListManuscripts.as_view(), name='list_manuscripts'),
    path('manuscripts/<int:pk>', views.ShowManuscript.as_view(), name='show_manuscript'),
    path('manuscripts/<int:pk>/reviews', views.ShowManuscriptReviews.as_view(), name='show_manuscript_reviews'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>', 
            views.ShowRevision.as_view(), name='show_revision'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>/reviews', 
            views.ShowRevisionReviews.as_view(), name='show_revision_reviews'),
    path('manuscripts/<int:manuscript_pk>/versions/<int:revision_number>/reviews/editorial', 
            views.EditRevisionEditorialReview.as_view(), name='edit_revision_editorial_review'),
    path('reviews', views.ListReviews.as_view(), name='list_reviews'),
    path('issues', views.ListIssues.as_view(), name='list_issues'),
    path('issues/new', views.NewIssue.as_view(), name='new_issue'),
    path('issues/<int:pk>', views.ShowIssue.as_view(), name='show_issue'),
    path('issues/<int:pk>/edit', views.EditIssue.as_view(), name='edit_issue'),
]


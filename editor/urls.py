from django.urls import path

from . import views

app_name = "editor"
urlpatterns = [
    path('', views.EditorHome.as_view(), name='home'),
    path('manuscripts', views.ListEditorManuscripts.as_view(), name='list_manuscripts'),
    path('manuscripts/<int:pk>', views.ShowEditorManuscript.as_view(), name='show_manuscript'),
    path('reviews', views.ListEditorReviews.as_view(), name='list_reviews'),
    path('issues', views.ListIssues.as_view(), name='list_issues'),
    path('issues/new', views.NewIssue.as_view(), name='new_issue'),
    path('issues/<int:pk>', views.ShowIssue.as_view(), name='show_issue'),
    path('issues/<int:pk>/edit', views.EditIssue.as_view(), name='edit_issue'),
]


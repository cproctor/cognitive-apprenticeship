from django_distill import distill_path as path
from editor.models import JournalIssue
from . import views

def get_all_issues():
    for issue in JournalIssue.objects.all():
        yield {'pk': issue.id}

app_name = "public"
urlpatterns = [
    path('', views.HomePage.as_view(), name='home_page'),
    path('issues/<int:pk>/', views.ShowIssue.as_view(), name='show_issue', distill_func=get_all_issues),
    #path('about', views.AboutPage.as_view(), name='about_page'),
]


from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    # /polls/
    path('', views.IndexView.as_view(), name='index'),
    # /polls/2/
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # /polls/2/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # /polls/2/vote/
    path('<int:question_id>/vote/', views.vote, name='vote')
]
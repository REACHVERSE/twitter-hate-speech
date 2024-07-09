from django.urls import path
from . import views

urlpatterns = [
    path("predict/", views.PredictView.as_view()),
    path("predictions/", views.PredictionListAPIView.as_view()),
    path("stats/", views.PredictionStatsView.as_view()),
    path("stats/graph/", views.PredictionCountByPredictionView.as_view()),
    path("reviews/post/", views.ReviewPostView.as_view()),
    path("reviews/list/", views.ReviewListView.as_view())
]
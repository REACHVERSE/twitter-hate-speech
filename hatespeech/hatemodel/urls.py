from django.urls import path
from . import views

urlpatterns = [
    path("predict/", views.PredictView.as_view()),
    path("predictions/", views.PredictionListAPIView.as_view()),
    path("predictions/<int:pk>/delete/", views.PredictionDeleteView.as_view()),
    path("pastweekgraph/", views.PredictionCountByPredictionView.as_view())
]
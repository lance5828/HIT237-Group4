from django.urls import path
from . import views

urlpatterns = [
    path("anomalies/", views.AnomalyListView.as_view(), name="anomaly-list"),
    path("anomalies/<int:pk>/", views.AnomalyDetailView.as_view(), name="anomaly-detail"),
    path("anomalies/create/", views.AnomalyCreateView.as_view(), name="anomaly-create"),
]


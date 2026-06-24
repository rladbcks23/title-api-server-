from django.urls import path

from .views import HealthView, TitleCreateView


urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("titles/", TitleCreateView.as_view(), name="title-create"),
]


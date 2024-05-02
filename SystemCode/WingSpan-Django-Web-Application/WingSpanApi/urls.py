from django.urls import path
from . import views
from .views import handlerequest

urlpatterns = [
    path("", views.index, name="index"),
    path("handlerequest/", handlerequest.as_view(), name="wingspan_api"),
]

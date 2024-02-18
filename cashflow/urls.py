from django.urls import path
from . import views

urlpatterns = [
    path("openings/",  views.opening_list),
    path("openings/<int:pk>/",  views.opening),
    path("transactions/",  views.transaction_list),
    path("transactions/<int:pk>/",  views.transaction),
]

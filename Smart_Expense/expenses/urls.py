from django.urls import path
from .views import (
    ExpenseListCreateAPIView,
    CategoryDetailAPIView,
)

urlpatterns = [
    path("expenses/", ExpenseListCreateAPIView.as_view(), name="api-expenses"),
    path(
        "categories/<int:pk>/",
        CategoryDetailAPIView.as_view(),
        name="api-category-detail",
    ),
]
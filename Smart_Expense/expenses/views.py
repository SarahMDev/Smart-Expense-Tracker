from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ExpenseSerializer
from .services import create_expense, list_expenses
from rest_framework.generics import RetrieveAPIView
from .models import Category
from .serializers import CategoryDetailSerializer


class ExpenseListCreateAPIView(APIView):
    def get(self, request):
        expenses = list_expenses()
        data = [
            {
                "id": item["id"],
                "title": item["title"],
                "amount": str(item["amount"]),
                "category": item["category__name"],
                "date": item["date"].isoformat(),
                "notes": item["notes"],
            }
            for item in expenses
        ]
        return Response(data)

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            expense = create_expense(
                title=data["title"],
                amount=data["amount"],
                category_name=data["category_name"],
                date=data["date"],
                notes=data.get("notes", ""),
            )
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "id": expense.id,
                "title": expense.title,
                "amount": str(expense.amount),
                "category": expense.category.name,
                "date": expense.date.isoformat(),
                "notes": expense.notes,
            },
            status=status.HTTP_201_CREATED,
        )


class CategoryDetailAPIView(RetrieveAPIView):
      queryset = Category.objects.all()
      serializer_class = CategoryDetailSerializer
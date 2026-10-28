from rest_framework import serializers
from .models import Category, Expense


class ExpenseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    category_name = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "amount",
            "category",
            "category_name",
            "date",
            "notes",
        ]
     
        read_only_fields = ["id", "category"]

class CategoryDetailSerializer(serializers.ModelSerializer):
    expenses = ExpenseSerializer(
    source="expense_set",
    many=True,
    read_only=True,
)

    class Meta:
        model = Category
        fields = ["id", "name", "expenses"]

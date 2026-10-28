from decimal import Decimal, InvalidOperation
from datetime import date
from calendar import monthrange
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .models import Category, Expense


def create_expense(title, amount, category_name, date, notes=""):
    if not title or not title.strip():
        raise ValidationError("Expense title cannot be empty.")

    if not category_name or not category_name.strip():
        raise ValidationError("Category name cannot be empty.")

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError("Amount must be a valid number.")

    if not amount.is_finite() or amount <= 0:
        raise ValidationError("Amount must be greater than zero.")

    category_name = category_name.strip()
    category = Category.objects.filter(
        name__iexact=category_name
    ).first()

    if category is None:
        category = Category.objects.create(name=category_name)

    expense = Expense(
        title=title.strip(),
        amount=amount,
        category=category,
        date=date,
        notes=notes or "",
    )

    expense.full_clean()
    expense.save()
    return expense


def get_total_expenses(start_date, end_date):
    total = Expense.objects.filter(
        date__range=(start_date, end_date)
    ).aggregate(total=Sum("amount"))["total"]

    return total if total is not None else Decimal("0.00")


def get_monthly_summary(year, month):
    if not 1 <= month <= 12:
        raise ValidationError("Month must be between 1 and 12.")

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    expenses = Expense.objects.filter(
        date__range=(start_date, end_date)
    )

    return {
        "year": year,
        "month": month,
        "total": get_total_expenses(start_date, end_date),
        "count": expenses.count(),
    }


def get_expenses_by_category(start_date, end_date):
    return list(
        Expense.objects.filter(
            date__range=(start_date, end_date)
        )
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )


def get_highest_expense(start_date=None, end_date=None):
    expenses = Expense.objects.select_related("category").all()

    if start_date is not None:
        expenses = expenses.filter(date__gte=start_date)

    if end_date is not None:
        expenses = expenses.filter(date__lte=end_date)

    expense = expenses.order_by("-amount", "-date").first()

    if expense is None:
        return None

    return {
        "id": expense.id,
        "title": expense.title,
        "amount": str(expense.amount),
        "category": expense.category.name if expense.category else None,
        "date": expense.date.isoformat(),
        "notes": expense.notes,
    }


def list_expenses(
    start_date=None,
    end_date=None,
    category_name=None,
    title=None,
):
    expenses = Expense.objects.select_related("category").all()

    if start_date is not None:
        expenses = expenses.filter(date__gte=start_date)

    if end_date is not None:
        expenses = expenses.filter(date__lte=end_date)

    if category_name:
        expenses = expenses.filter(
            category__name__iexact=category_name.strip()
        )

    if title:
        expenses = expenses.filter(title__icontains=title.strip())

    return list(
        expenses.order_by("-date", "-id").values(
            "id",
            "title",
            "amount",
            "category__name",
            "date",
            "notes",
        )
    )




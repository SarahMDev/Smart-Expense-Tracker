from datetime import date
from decimal import Decimal, InvalidOperation
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from mcp.server.fastmcp import FastMCP

from expenses.services import (
    create_expense,
    get_total_expenses as calculate_total_expenses,
    get_monthly_summary,
    get_expenses_by_category,
    get_highest_expense,
    list_expenses,
)


def add_expense_sync(title, amount, category_name, expense_date, notes):
    parsed_date = date.fromisoformat(expense_date)

    expense = create_expense(
        title=title,
        amount=Decimal(str(amount)),
        category_name=category_name,
        date=parsed_date,
        notes=notes,
    )

    return {
        "id": expense.id,
        "title": expense.title,
        "amount": str(expense.amount),
        "category": expense.category.name,
        "date": expense.date.isoformat(),
        "notes": expense.notes,
    }


def get_expenses_sync(start_date, end_date, category_name, title):
    expenses = list_expenses(
        start_date=start_date,
        end_date=end_date,
        category_name=category_name or None,
        title=title or None,
    )

    return [
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


def monthly_summary_sync(year, month):
    summary = get_monthly_summary(year, month)
    return {
        "year": summary["year"],
        "month": summary["month"],
        "total": str(summary["total"]),
        "count": summary["count"],
    }


def category_summary_sync(start_date, end_date):
    rows = get_expenses_by_category(start_date, end_date)
    return [
        {
            "category": row["category__name"],
            "total": str(row["total"] or 0),
        }
        for row in rows
    ]


def highest_expense_sync(start_date, end_date):
    expense = get_highest_expense(start_date, end_date)
    if expense is None:
        return None
    return expense


def register_tools(mcp: FastMCP):
    """Register expense-management tools on the shared MCP server."""

    @mcp.tool()
    async def add_expense(
        title: str,
        amount: float,
        category_name: str,
        expense_date: str,
        notes: str = "",
    ) -> dict:
        """Add an expense. Use YYYY-MM-DD for the date."""
        try:
            expense = await sync_to_async(
                add_expense_sync,
                thread_sensitive=True,
            )(title, amount, category_name, expense_date, notes)

            return {
                "success": True,
                "message": "Expense added successfully.",
                "expense": expense,
            }
        except (ValueError, InvalidOperation, ValidationError) as exc:
            return {"success": False, "error": str(exc)}
        except Exception:
            return {
                "success": False,
                "error": "Could not add the expense. Check server logs.",
            }

    @mcp.tool()
    async def get_expenses(
        start_date: str = "",
        end_date: str = "",
        category_name: str = "",
        title: str = "",
    ) -> dict:
        """List expenses with optional date, category, and title filters."""
        try:
            parsed_start = date.fromisoformat(start_date) if start_date else None
            parsed_end = date.fromisoformat(end_date) if end_date else None

            if parsed_start and parsed_end and parsed_start > parsed_end:
                return {
                    "success": False,
                    "error": "start_date must be on or before end_date.",
                }

            expenses = await sync_to_async(
                get_expenses_sync,
                thread_sensitive=True,
            )(parsed_start, parsed_end, category_name, title)

            return {
                "success": True,
                "count": len(expenses),
                "expenses": expenses,
            }
        except ValueError as exc:
            return {"success": False, "error": f"Invalid input: {exc}"}
        except Exception:
            return {
                "success": False,
                "error": "Could not retrieve expenses. Check server logs.",
            }

    @mcp.tool()
    async def get_monthly_summary(year: int, month: int) -> dict:
        """Get total spending and expense count for a month."""
        try:
            return await sync_to_async(
                monthly_summary_sync,
                thread_sensitive=True,
            )(year, month)
        except (ValueError, ValidationError) as exc:
            return {"success": False, "error": str(exc)}
        except Exception:
            return {
                "success": False,
                "error": "Could not calculate monthly summary. Check server logs.",
            }

    @mcp.tool()
    async def get_expenses_by_category(
        start_date: str,
        end_date: str,
    ) -> dict:
        """Get spending totals grouped by category for a date range."""
        try:
            parsed_start = date.fromisoformat(start_date)
            parsed_end = date.fromisoformat(end_date)

            if parsed_start > parsed_end:
                return {
                    "success": False,
                    "error": "start_date must be on or before end_date.",
                }

            rows = await sync_to_async(
                category_summary_sync,
                thread_sensitive=True,
            )(parsed_start, parsed_end)

            return {"success": True, "categories": rows}
        except ValueError as exc:
            return {"success": False, "error": f"Invalid input: {exc}"}
        except Exception:
            return {
                "success": False,
                "error": "Could not calculate category totals. Check server logs.",
            }

    @mcp.tool()
    async def get_highest_expense(
        start_date: str = "",
        end_date: str = "",
    ) -> dict:
        """Find the single highest-value expense in an optional date range."""
        try:
            parsed_start = date.fromisoformat(start_date) if start_date else None
            parsed_end = date.fromisoformat(end_date) if end_date else None

            if parsed_start and parsed_end and parsed_start > parsed_end:
                return {
                    "success": False,
                    "error": "start_date must be on or before end_date.",
                }

            expense = await sync_to_async(
                highest_expense_sync,
                thread_sensitive=True,
            )(parsed_start, parsed_end)

            return {
                "success": True,
                "expense": expense,
            }
        except ValueError as exc:
            return {"success": False, "error": f"Invalid input: {exc}"}
        except Exception:
            return {
                "success": False,
                "error": "Could not find the highest expense. Check server logs.",
            }

    @mcp.tool()
    async def get_total_expenses(
        start_date: str,
        end_date: str,
    ) -> dict:
        """Calculate total spending between two dates."""
        try:
            parsed_start = date.fromisoformat(start_date)
            parsed_end = date.fromisoformat(end_date)

            if parsed_start > parsed_end:
                return {
                    "success": False,
                    "error": "start_date must be on or before end_date.",
                }

            total = await sync_to_async(
                calculate_total_expenses,
                thread_sensitive=True,
            )(parsed_start, parsed_end)

            return {"success": True, "total": str(total)}
        except ValueError as exc:
            return {"success": False, "error": f"Invalid input: {exc}"}
        except Exception:
            return {
                "success": False,
                "error": "Could not calculate total spending. Check server logs.",
            }

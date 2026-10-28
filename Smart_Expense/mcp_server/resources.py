import json
from asgiref.sync import sync_to_async
from mcp.server.fastmcp import FastMCP

from expenses.services import list_expenses


def list_expenses_resource_sync():
    """Read and serialize expenses inside Django's synchronous context."""
    expenses = list_expenses()

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


def register_resources(mcp: FastMCP):
    """Register MCP resources on the shared FastMCP server."""

    @mcp.resource("expenses://all")
    async def all_expenses_resource() -> str:
        """Return all saved expenses as JSON."""
        try:
            results = await sync_to_async(
                list_expenses_resource_sync,
                thread_sensitive=True,
            )()

            return json.dumps(results, ensure_ascii=False)

        except Exception:
            # Keep database and internal details out of resource error messages.
            return json.dumps(
                {
                    "success": False,
                    "error": "Could not retrieve expenses. Check the server logs.",
                },
                ensure_ascii=False,
            )

import os
import sys
from pathlib import Path

import django
from mcp.server.fastmcp import FastMCP


# Configure Django before importing the project services.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "Smart_Expense.settings",
)
django.setup()


# Create one shared MCP server.
mcp = FastMCP("Smart Expense Tracker")


# Register tools, resources, and prompts on the same server.
from mcp_server.tools import register_tools
from mcp_server.resources import register_resources
from mcp_server.prompts import register_prompts

register_tools(mcp)
register_resources(mcp)
register_prompts(mcp)


if __name__ == "__main__":
    mcp.run(transport="stdio")


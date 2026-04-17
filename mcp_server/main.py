# mcp_server/main.py

from fastmcp import FastMCP

# import tools
from mcp_server.tools.math_tools import add, multiply, subtract, divide
from mcp_server.tools.time_tools import get_current_time, get_current_date
from mcp_server.tools.text_tools import (
    to_uppercase, to_lowercase, word_count, reverse_text
)
from mcp_server.tools.expense_tools import add_expense, get_expenses

mcp = FastMCP("multi-agent-mcp")

# Math tools
mcp.tool(name="add_numbers", description="Add two numbers")(add)
mcp.tool(name="multiply_numbers", description="Multiply two numbers")(multiply)
mcp.tool(name="subtract_numbers", description="Subtract two numbers")(subtract)
mcp.tool(name="divide_numbers", description="Divide two numbers")(divide)

# Time tools
mcp.tool(name="get_current_time", description="Get current time")(get_current_time)
mcp.tool(name="get_current_date", description="Get current date")(get_current_date)

# Text tools
mcp.tool(name="uppercase_text", description="Convert text to uppercase")(to_uppercase)
mcp.tool(name="lowercase_text", description="Convert text to lowercase")(to_lowercase)
mcp.tool(name="word_count", description="Count words in text")(word_count)
mcp.tool(name="reverse_text", description="Reverse text")(reverse_text)

# Expense tools
mcp.tool(name="add_expense", description="Add expense for user")(add_expense)
mcp.tool(name="get_expenses", description="Get all expenses for user")(get_expenses)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)
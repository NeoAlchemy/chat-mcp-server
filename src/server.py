import random
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Chat-MCP-Server", host="0.0.0.0", port=8001)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    print(f"[debug-server] add({a}, {b})")
    return a + b

@mcp.tool()
def get_secret_word() -> str:
    print("[debug-server] get_secret_word()")
    return random.choice(["apple", "banana", "cherry"])

@mcp.tool()
def get_current_weather(city: str) -> str:
    print(f"[debug-server] get_current_weather({city})")
    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text

if __name__ == "__server__":
    mcp.run(transport="sse")

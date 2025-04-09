import random
import requests
import mcp

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

app = FastAPI()

mcp = FastMCP("Chat-MCP-Server")

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

app.mount("/", mcp.sse_app())
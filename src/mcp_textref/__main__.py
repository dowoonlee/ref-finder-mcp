"""MCP 서버 진입점 (python -m mcp_textref)"""

from .server import mcp

if __name__ == "__main__":
    mcp.run()

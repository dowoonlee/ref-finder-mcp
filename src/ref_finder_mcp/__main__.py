"""MCP 서버 진입점 (python -m ref_finder_mcp)"""

from .server import mcp

if __name__ == "__main__":
    mcp.run()

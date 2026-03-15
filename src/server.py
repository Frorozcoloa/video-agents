from fastmcp import FastMCP
from features.hello_world.tool import register_hello_world

# Initialize FastMCP server
mcp = FastMCP("Video Agents")

# Register features
register_hello_world(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")

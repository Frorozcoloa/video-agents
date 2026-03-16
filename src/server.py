from fastmcp import FastMCP
from features.hello_world.tool import register_hello_world
from features.audio_extraction.tool import register_audio_extraction

# Initialize FastMCP server
mcp = FastMCP("Video Agents")

# Register features
register_hello_world(mcp)
register_audio_extraction(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")

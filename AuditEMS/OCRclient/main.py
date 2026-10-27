import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

SERVERS = {
    "ocr": {
        "transport": "stdio",
        "command": "/snap/bin/uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "/home/swaraj/projects/AuditEMS/OCRserver/main.py",
            # path for the server which we want to run
        ],
    }
}

async def main():
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    print(tools)

if __name__ == "__main__":
    asyncio.run(main())

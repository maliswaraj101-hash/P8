SERVERS = {
    "ocr": {
        "transport": "stdio",
        "command": "/snap/bin/uv",
        "args": [
            "run",
            "--project",
            "/home/swaraj/projects/AuditEMS/OCRserver",
            "python3",
            "/home/swaraj/projects/AuditEMS/OCRserver/main.py"
        ]
    }
}

# suppose u integrate 5 github tools from github write their code using mcp.tool , this is normal langgraph tools , for every version change in github we will have to change code for the tool implementation , so instead of doing this we can use mcp servers. 
# mcp servers have the tools , so github mcp server will have their own tools they will maintain it we will just have the config file which is this file on the client side.
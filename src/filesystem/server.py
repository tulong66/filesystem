import asyncio
import os
import shutil
import fnmatch
from pathlib import Path
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

server = Server("filesystem")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available file system resources.
    """
    return [
        types.Resource(
            uri=AnyUrl("file://system"),
            name="File System Operations",
            description="Interface for file system operations",
            mimeType="application/json",
        )
    ]

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="read_file",
            description="Read complete contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name="read_multiple_files",
            description="Read multiple files simultaneously",
            inputSchema={
                "type": "object",
                "properties": {
                    "paths": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["paths"],
            },
        ),
        types.Tool(
            name="write_file",
            description="Create new file or overwrite existing (exercise caution with this)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        ),
        types.Tool(
            name="create_directory",
            description="Create new directory or ensure it exists",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name="list_directory",
            description="List directory contents with [FILE] or [DIR] prefixes",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name="move_file",
            description="Move or rename files and directories",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["source", "destination"],
            },
        ),
        types.Tool(
            name="search_files",
            description="Recursively search for files/directories",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "pattern": {"type": "string"},
                    "excludePatterns": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["path", "pattern"],
            },
        ),
        types.Tool(
            name="get_file_info",
            description="Get detailed file/directory metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name="list_allowed_directories",
            description="List all directories the server is allowed to access",
            inputSchema={
                "type": "object",
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name == "read_file":
        path = arguments.get("path")
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            return [
                types.TextContent(
                    type="text",
                    text=content,
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error reading file: {str(e)}",
                )
            ]

    elif name == "read_multiple_files":
        paths = arguments.get("paths")
        results = []
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                results.append(
                    types.TextContent(
                        type="text",
                        text=content,
                    )
                )
            except Exception as e:
                results.append(
                    types.TextContent(
                        type="text",
                        text=f"Error reading file {path}: {str(e)}",
                    )
                )
        return results

    elif name == "write_file":
        path = arguments.get("path")
        content = arguments.get("content")
        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
            return [
                types.TextContent(
                    type="text",
                    text=f"File written to {path}",
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error writing file: {str(e)}",
                )
            ]

    elif name == "create_directory":
        path = arguments.get("path")
        try:
            os.makedirs(path, exist_ok=True)
            return [
                types.TextContent(
                    type="text",
                    text=f"Directory created at {path}",
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error creating directory: {str(e)}",
                )
            ]

    elif name == "list_directory":
        path = arguments.get("path")
        try:
            items = os.listdir(path)
            result = "\n".join([f"[FILE] {item}" if os.path.isfile(os.path.join(path, item)) else f"[DIR] {item}" for item in items])
            return [
                types.TextContent(
                    type="text",
                    text=result,
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error listing directory: {str(e)}",
                )
            ]

    elif name == "move_file":
        source = arguments.get("source")
        destination = arguments.get("destination")
        try:
            shutil.move(source, destination)
            return [
                types.TextContent(
                    type="text",
                    text=f"Moved {source} to {destination}",
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error moving file: {str(e)}",
                )
            ]

    elif name == "search_files":
        path = arguments.get("path")
        pattern = arguments.get("pattern")
        exclude_patterns = arguments.get("excludePatterns", [])
        try:
            matches = []
            for root, dirs, files in os.walk(path):
                for item in files + dirs:
                    if any(fnmatch.fnmatch(item, exclude) for exclude in exclude_patterns):
                        continue
                    if fnmatch.fnmatch(item, pattern):
                        matches.append(os.path.join(root, item))
            return [
                types.TextContent(
                    type="text",
                    text="\n".join(matches),
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error searching files: {str(e)}",
                )
            ]

    elif name == "get_file_info":
        path = arguments.get("path")
        try:
            file_stats = os.stat(path)
            info = {
                "size": file_stats.st_size,
                "creation_time": file_stats.st_ctime,
                "modified_time": file_stats.st_mtime,
                "access_time": file_stats.st_atime,
                "type": "file" if os.path.isfile(path) else "directory",
                "permissions": oct(file_stats.st_mode)[-3:],
            }
            return [
                types.TextContent(
                    type="text",
                    text=str(info),
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error getting file info: {str(e)}",
                )
            ]

    elif name == "list_allowed_directories":
        # Implement logic to list allowed directories
        return [
            types.TextContent(
                type="text",
                text="List of allowed directories",
            )
        ]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="filesystem",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

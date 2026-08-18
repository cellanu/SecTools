"""
Terminal MCP Server - Main Entry Point

This is the main server module that implements the MCP protocol
and exposes terminal command execution as an MCP tool.
"""

import asyncio
import json
import sys
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

# Import our modules
from tools.terminal import execute_command, CommandResult
from security.filter import get_filter, CommandFilter


def create_execute_command_tool() -> Tool:
    """Create the execute_command MCP tool definition."""
    return Tool(
        name="execute_command",
        description=(
            "Execute a terminal command on the local system and return the execution results. "
            "Supports Windows (PowerShell/CMD), Linux (Bash), and macOS (Bash/Zsh). "
            "Commands are validated against security policies before execution."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The terminal command to execute"
                },
                "working_directory": {
                    "type": "string",
                    "description": "The directory where the command should be executed (optional, defaults to server working directory)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum execution time in seconds (optional, defaults to 30 seconds)"
                }
            },
            "required": ["command"]
        }
    )


async def handle_execute_command(arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle the execute_command tool call.
    
    Args:
        arguments: Tool call arguments from MCP client.
        
    Returns:
        List of TextContent with the execution result.
    """
    # Extract arguments
    command = arguments.get("command", "")
    working_directory = arguments.get("working_directory")
    timeout = arguments.get("timeout")
    
    if not command:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": "Error: 'command' parameter is required",
                "execution_time": 0.0
            }, indent=2)
        )]
    
    # Execute the command
    result = await execute_command(
        command=command,
        working_directory=working_directory,
        timeout=timeout
    )
    
    # Format result as JSON
    result_dict = {
        "success": result.success,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "execution_time": round(result.execution_time, 3)
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result_dict, indent=2, ensure_ascii=False)
    )]


async def main():
    """Main entry point for the MCP server."""
    # Initialize the server
    server = Server("terminal-mcp-server")
    
    # Get security filter (loads config automatically)
    filter_instance = get_filter()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [create_execute_command_tool()]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        if name == "execute_command":
            return await handle_execute_command(arguments)
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}"
                })
            )]
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown requested...", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

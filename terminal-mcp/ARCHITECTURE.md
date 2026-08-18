# Terminal MCP Server - Architecture Design

## 1. Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Client                             │
│  (Claude Desktop / Cursor / Continue / etc.)                │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ MCP Protocol (stdio/SSE)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (server.py)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              MCP Protocol Handler                      │  │
│  │  - List Tools                                          │  │
│  │  - Call Tool                                           │  │
│  │  - Error Handling                                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Security Layer (security/filter.py)        │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Command Filter  │  │ Config Manager  │                  │
│  │ - Blacklist     │  │ - Load YAML     │                  │
│  │ - Whitelist     │  │ - Validate      │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Tool Implementation (tools/terminal.py)       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              execute_command                           │  │
│  │  - Async subprocess execution                          │  │
│  │  - Timeout control                                     │  │
│  │  - Output capture                                      │  │
│  │  - Error handling                                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    System Shell                              │
│  Windows: PowerShell / CMD                                   │
│  Linux:   Bash                                               │
│  macOS:   Bash / Zsh                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Audit Logs (logs/)                        │
│  - Execution records                                         │
│  - Security events                                           │
│  - Error logs                                                │
└─────────────────────────────────────────────────────────────┘
```

## 2. Component Responsibilities

### server.py (Main Entry Point)
- Initialize MCP server with stdio transport
- Register tools
- Handle MCP protocol messages
- Global exception handling

### tools/terminal.py (Tool Implementation)
- Implement `execute_command` tool
- Async subprocess management
- Output encoding handling
- Timeout and process termination

### security/filter.py (Security Layer)
- Load and validate configuration
- Command blacklist/whitelist filtering
- Dangerous pattern detection
- Security audit logging

### config/config.yaml (Configuration)
- Security policies
- Allowed/denied commands
- Timeout limits
- Log settings

## 3. Data Flow

1. Client sends `tools/call` request with `execute_command`
2. Server receives request and extracts parameters
3. Security filter validates the command
4. If approved, execute via async subprocess
5. Capture stdout, stderr, exit code
6. Log execution details
7. Return structured result to client

## 4. Security Considerations

- All commands pass through security filter before execution
- Configurable whitelist/blacklist
- Maximum timeout enforcement
- Audit logging for all executions
- Dangerous command pattern detection
- Working directory validation

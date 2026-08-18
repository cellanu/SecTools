# Terminal MCP Server - Tool API Design

## 1. MCP Tool Definition

### Tool: execute_command

**Description:** Execute a terminal command on the local system and return the execution results.

**Input Schema:**
```json
{
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
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the command executed successfully"
    },
    "exit_code": {
      "type": "integer",
      "description": "The exit code of the command"
    },
    "stdout": {
      "type": "string",
      "description": "Standard output from the command"
    },
    "stderr": {
      "type": "string",
      "description": "Standard error output from the command"
    },
    "execution_time": {
      "type": "number",
      "description": "Execution time in seconds"
    }
  }
}
```

## 2. Error Responses

### Command Blocked by Security Filter
```json
{
  "success": false,
  "exit_code": -1,
  "stdout": "",
  "stderr": "Command blocked by security filter: <reason>",
  "execution_time": 0.0
}
```

### Timeout Error
```json
{
  "success": false,
  "exit_code": -2,
  "stdout": "<partial output>",
  "stderr": "Command timed out after <timeout> seconds",
  "execution_time": <timeout>
}
```

### Command Not Found
```json
{
  "success": false,
  "exit_code": 127,
  "stdout": "",
  "stderr": "Command not found: <command>",
  "execution_time": <actual_time>
}
```

### Permission Denied
```json
{
  "success": false,
  "exit_code": 126,
  "stdout": "",
  "stderr": "Permission denied: <command>",
  "execution_time": <actual_time>
}
```

## 3. Security Configuration API

### config.yaml Structure
```yaml
security:
  enable_command_filter: true
  
  # Whitelist mode: only these commands are allowed
  allow_commands:
    - python
    - git
    - docker
    - npm
    - node
    - pip
    - ls
    - pwd
    - echo
    - cat
    
  # Blacklist: these commands are always denied
  deny_commands:
    - rm
    - shutdown
    - reboot
    - format
    - del
    
  # Maximum allowed timeout (seconds)
  max_timeout: 300
  
  # Dangerous patterns (regex)
  dangerous_patterns:
    - "rm\\s+-rf\\s+/"
    - "dd\\s+if="
    - "mkfs"
    - ":\\(\\)\\s*\\{"  # fork bomb
    
  # Working directory restrictions
  allowed_directories:
    - /home/user/projects
    - /tmp
    
logging:
  level: INFO
  file: logs/audit.log
  max_size_mb: 100
  backup_count: 5
```

## 4. Audit Log Format

Each execution is logged with:
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "client_id": "mcp-client-001",
  "command": "git status",
  "working_directory": "/home/user/project",
  "timeout": 30,
  "success": true,
  "exit_code": 0,
  "execution_time": 0.523,
  "stdout_preview": "On branch main...",
  "stderr_preview": ""
}
```

## 5. Future Extension Points

### File Operations (Reserved)
```python
# tools/files.py
async def read_file(path: str) -> str
async def write_file(path: str, content: str) -> bool
async def list_directory(path: str) -> list[str]
```

### Docker Management (Reserved)
```python
# tools/docker.py
async def docker_ps() -> list[dict]
async def docker_exec(container: str, command: str) -> dict
```

### Git Operations (Reserved)
```python
# tools/git.py
async def git_status(repo_path: str) -> str
async def git_diff(repo_path: str) -> str
```

### System Information (Reserved)
```python
# tools/system.py
async def system_info() -> dict
async def disk_usage() -> dict
async def process_list() -> list[dict]
```

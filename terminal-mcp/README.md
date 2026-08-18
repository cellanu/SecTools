# Terminal MCP Server

一个安全的本地终端命令执行 MCP (Model Context Protocol) 服务器。

## 功能特性

- ✅ **终端命令执行**: 通过 MCP 协议安全地执行本地终端命令
- ✅ **跨平台支持**: Windows (PowerShell/CMD), Linux (Bash), macOS (Bash/Zsh)
- ✅ **安全控制**: 命令白名单/黑名单、危险模式检测、目录限制
- ✅ **异步执行**: 基于 asyncio，支持超时控制和进程终止
- ✅ **审计日志**: 所有命令执行记录自动保存
- ✅ **可配置**: YAML 配置文件，灵活的安全策略

## 项目结构

```
terminal-mcp/
├── server.py              # MCP 服务器主入口
├── tools/
│   └── terminal.py        # 终端命令执行工具
├── security/
│   └── filter.py          # 安全过滤器
├── config/
│   └── config.yaml        # 安全配置文件
├── logs/                  # 审计日志目录
├── requirements.txt       # Python 依赖
├── ARCHITECTURE.md        # 架构设计文档
├── API_DESIGN.md          # API 设计文档
└── README.md              # 本文件
```

## 安装步骤

### 1. 环境要求

- Python 3.11+
- pip

### 2. 安装依赖

```bash
cd terminal-mcp
pip install -r requirements.txt
```

### 3. 验证安装

```bash
python -c "import mcp; print('MCP SDK installed')"
```

## 配置说明

编辑 `config/config.yaml` 文件配置安全策略：

```yaml
security:
  # 启用命令过滤
  enable_command_filter: true
  
  # 白名单：只允许这些命令（留空禁用白名单）
  allow_commands:
    - python
    - git
    - docker
    - npm
    - node
    
  # 黑名单：始终禁止的命令
  deny_commands:
    - rm
    - shutdown
    - reboot
    - sudo
    
  # 最大超时时间（秒）
  max_timeout: 300
  
  # 默认超时时间（秒）
  default_timeout: 30
  
  # 危险命令模式（正则表达式）
  dangerous_patterns:
    - "rm\\s+-rf\\s+/"
    - "dd\\s+if="
    - "mkfs"
    
  # 禁止的目录
  forbidden_directories:
    - /etc
    - /root
    - /boot
```

## 运行服务器

```bash
cd terminal-mcp
python server.py
```

服务器将通过 stdio 与 MCP 客户端通信。

## MCP 客户端配置

### 📖 完整配置指南

详细配置文档请查看：

- **[CLIENT_CONFIG.md](CLIENT_CONFIG.md)** - ChatGPT、Qwen Chat、Claude、Cursor、Continue 等完整配置步骤
- **[configs/](configs/)** - 预配置的 JSON 模板文件

### 快速配置

1. **复制配置文件**

   ```bash
   cd configs
   
   # ChatGPT Desktop
   cp chatgpt_config.json ~/Library/Application\ Support/ChatGPT/mcp_config.json  # macOS
   # 或 %APPDATA%\ChatGPT\mcp_config.json (Windows)
   
   # Qwen Chat (通义千问)
   cp qwen_config.json ~/Library/Application\ Support/QwenChat/config.json  # macOS
   # 或 %APPDATA%\QwenChat\config.json (Windows)
   
   # Claude Desktop
   cp claude_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json  # macOS
   # 或 %APPDATA%\Claude\claude_desktop_config.json (Windows)
   ```

2. **编辑路径**

   打开配置文件，将 `/ABSOLUTE/PATH/TO/terminal-mcp` 替换为你的实际路径。

3. **重启 Client 应用**

### 各 Client 配置示例

#### Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) 或 `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "terminal": {
      "command": "python",
      "args": ["/path/to/terminal-mcp/server.py"],
      "cwd": "/path/to/terminal-mcp"
    }
  }
}
```

#### ChatGPT Desktop

编辑 `~/Library/Application Support/ChatGPT/mcp_config.json` (macOS) 或 `%APPDATA%\ChatGPT\mcp_config.json` (Windows):

```json
{
  "mcpServers": {
    "terminal": {
      "command": "python3",
      "args": ["/path/to/terminal-mcp/server.py"],
      "cwd": "/path/to/terminal-mcp",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

#### Qwen Chat (通义千问)

编辑 `~/Library/Application Support/QwenChat/config.json` (macOS) 或 `%APPDATA%\QwenChat\config.json` (Windows):

```json
{
  "mcp": {
    "enabled": true,
    "servers": {
      "terminal": {
        "type": "stdio",
        "command": "python3",
        "args": ["/path/to/terminal-mcp/server.py"],
        "cwd": "/path/to/terminal-mcp",
        "env": {
          "PYTHONIOENCODING": "utf-8",
          "LANG": "zh_CN.UTF-8"
        }
      }
    }
  }
}
```

#### Cursor

在 Cursor 设置中添加 MCP 服务器：

```json
{
  "cursor.mcp.servers": {
    "terminal": {
      "command": "python",
      "args": ["/path/to/terminal-mcp/server.py"],
      "cwd": "/path/to/terminal-mcp"
    }
  }
}
```

#### Continue

编辑 `.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "terminal",
      "command": "python",
      "args": ["/path/to/terminal-mcp/server.py"],
      "cwd": "/path/to/terminal-mcp"
    }
  ]
}
```

## 工具使用

### execute_command

执行终端命令并返回结果。

**参数:**
- `command` (string, 必填): 要执行的命令
- `working_directory` (string, 可选): 执行目录
- `timeout` (integer, 可选): 超时时间（秒）

**返回:**
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "command output",
  "stderr": "",
  "execution_time": 0.523
}
```

**示例:**

```python
# 基本用法
execute_command(command="ls -la")

# 指定目录
execute_command(command="git status", working_directory="/path/to/repo")

# 设置超时
execute_command(command="npm install", timeout=120)
```

## 测试案例

### 1. 基本命令测试

```bash
# 测试 echo 命令
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"execute_command","arguments":{"command":"echo Hello World"}},"id":1}' | python server.py
```

### 2. 安全过滤测试

```bash
# 测试黑名单命令（应被阻止）
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"execute_command","arguments":{"command":"rm -rf /"}},"id":1}' | python server.py
```

### 3. 超时测试

```bash
# 测试超时（sleep 超过指定时间）
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"execute_command","arguments":{"command":"sleep 10","timeout":2}},"id":1}' | python server.py
```

### 4. 完整测试脚本

创建 `test_mcp.py`:

```python
#!/usr/bin/env python3
"""Test script for Terminal MCP Server."""

import asyncio
import sys
sys.path.insert(0, '.')

from tools.terminal import execute_command
from security.filter import get_filter

async def test_basic_command():
    """Test basic command execution."""
    result = await execute_command("echo 'Hello World'")
    assert result.success, f"Command failed: {result.stderr}"
    assert "Hello World" in result.stdout
    print("✓ Basic command test passed")

async def test_security_filter():
    """Test security filtering."""
    filter_instance = get_filter()
    
    # Test blacklist
    validation = filter_instance.validate_command("rm -rf /")
    assert not validation.is_valid, "Blacklist should block rm command"
    print("✓ Security filter test passed")

async def test_timeout():
    """Test timeout handling."""
    result = await execute_command("sleep 5", timeout=1)
    assert not result.success, "Should timeout"
    assert result.exit_code == -2, "Timeout exit code should be -2"
    print("✓ Timeout test passed")

async def main():
    """Run all tests."""
    print("Running Terminal MCP Server tests...\n")
    
    await test_basic_command()
    await test_security_filter()
    await test_timeout()
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
```

运行测试:

```bash
python test_mcp.py
```

## 审计日志

所有命令执行记录保存在 `logs/audit.log`:

```
2024-01-15 10:30:45 - INFO - AUDIT | CMD: git status | DIR: /home/user/project | TIMEOUT: 30s | STATUS: SUCCESS | EXIT: 0 | DURATION: 0.523s | STDOUT: On branch main... | STDERR: 
2024-01-15 10:31:02 - WARNING - AUDIT | CMD: rm -rf / | DIR: . | TIMEOUT: 30s | STATUS: FAILED | EXIT: -1 | DURATION: 0.001s | STDOUT:  | STDERR: Command blocked by security filter
```

## 扩展开发

### 添加新工具

1. 在 `tools/` 目录创建新模块
2. 实现异步函数
3. 在 `server.py` 中注册工具

### 预留扩展点

代码已预留以下扩展接口：

- **文件操作**: `read_file`, `write_file`, `list_directory`
- **Docker 管理**: `docker_ps`, `docker_exec`
- **Git 操作**: `git_status`, `git_diff`
- **系统信息**: `system_info`, `disk_usage`, `process_list`

## 安全注意事项

⚠️ **重要**: 此工具允许执行任意系统命令，请确保：

1. 仔细配置白名单/黑名单
2. 在生产环境中限制可用命令
3. 定期审查审计日志
4. 不要以 root/管理员权限运行
5. 限制可访问的目录

## 故障排除

### 常见问题

**Q: 命令执行失败，提示 "Command not found"**
A: 检查命令是否在白名单中，或确认命令在系统 PATH 中。

**Q: 命令被安全过滤器阻止**
A: 查看 `logs/audit.log` 了解具体原因，调整 `config.yaml` 配置。

**Q: 中文输出乱码**
A: 工具会自动尝试多种编码，如需调整可修改 `_decode_output` 函数。

**Q: 长时间运行的命令被终止**
A: 增加 `timeout` 参数或调整配置的 `max_timeout`。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

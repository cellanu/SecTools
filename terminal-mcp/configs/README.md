# 快速配置脚本

本目录包含各大 MCP Client 的配置模板文件。

## 配置文件列表

| 文件名 | 适用 Client | 说明 |
|--------|-----------|------|
| `chatgpt_config.json` | ChatGPT Desktop | OpenAI ChatGPT 桌面版配置 |
| `qwen_config.json` | Qwen Chat (通义千问) | 阿里云通义千问配置 |
| `claude_config.json` | Claude Desktop | Anthropic Claude 桌面版配置 |
| `cursor_config.json` | Cursor | Cursor IDE 配置 |
| `continue_config.json` | Continue | VS Code / JetBrains Continue 插件配置 |

## 使用步骤

### 1. 获取项目绝对路径

```bash
# Linux/macOS
cd /path/to/terminal-mcp
pwd

# Windows PowerShell
Set-Location C:\path\to\terminal-mcp
Get-Location
```

### 2. 编辑配置文件

选择适合你的 Client 的配置文件，将以下占位符替换为实际路径：

```
/ABSOLUTE/PATH/TO/terminal-mcp
```

**示例（macOS/Linux）：**
```json
{
  "mcpServers": {
    "terminal": {
      "command": "python3",
      "args": ["/Users/username/projects/terminal-mcp/server.py"],
      "cwd": "/Users/username/projects/terminal-mcp"
    }
  }
}
```

**示例（Windows）：**
```json
{
  "mcpServers": {
    "terminal": {
      "command": "C:\\Python311\\python.exe",
      "args": ["C:\\Users\\username\\projects\\terminal-mcp\\server.py"],
      "cwd": "C:\\Users\\username\\projects\\terminal-mcp"
    }
  }
}
```

### 3. 复制到 Client 配置目录

#### ChatGPT Desktop

```bash
# macOS
cp chatgpt_config.json ~/Library/Application\ Support/ChatGPT/mcp_config.json

# Windows (PowerShell)
Copy-Item chatgpt_config.json "$env:APPDATA\ChatGPT\mcp_config.json"

# Linux
cp chatgpt_config.json ~/.config/ChatGPT/mcp_config.json
```

#### Qwen Chat (通义千问)

```bash
# macOS
cp qwen_config.json ~/Library/Application\ Support/QwenChat/config.json

# Windows (PowerShell)
Copy-Item qwen_config.json "$env:APPDATA\QwenChat\config.json"

# Linux
cp qwen_config.json ~/.config/QwenChat/config.json
```

#### Claude Desktop

```bash
# macOS
cp claude_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows (PowerShell)
Copy-Item claude_config.json "$env:APPDATA\Claude\claude_desktop_config.json"

# Linux
mkdir -p ~/.config/claude
cp claude_config.json ~/.config/claude/claude_desktop_config.json
```

#### Cursor

打开 Cursor 设置 (`Cmd/Ctrl + ,`) → 搜索 "MCP" → 粘贴配置内容到相应位置。

或者编辑 settings.json：

```bash
# macOS
# 在 Cursor 中按 Cmd+Shift+P，输入 "Open Settings (JSON)"
# 然后粘贴 cursor_config.json 的内容

# 或手动编辑
nano ~/Library/Application\ Support/Cursor/User/settings.json
```

#### Continue

```bash
# VS Code 项目级别配置
mkdir -p .continue
cp continue_config.json .continue/config.json
```

或在 VS Code 中：
1. 按 `Cmd/Ctrl + Shift + P`
2. 输入 "Continue: Open Config"
3. 粘贴配置内容

### 4. 重启 Client 应用

配置完成后，完全退出并重新启动对应的 Client 应用。

### 5. 验证配置

在 Client 中尝试以下命令：

```
列出当前目录的文件
```

如果配置正确，Client 应该能够调用 `execute_command` 工具执行命令。

## 故障排除

### 检查配置文件语法

```bash
# 使用 Python 验证 JSON
python -m json.tool chatgpt_config.json > /dev/null && echo "JSON valid" || echo "JSON invalid"
```

### 测试 MCP Server

```bash
cd /path/to/terminal-mcp
echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | python server.py
```

### 查看日志

```bash
tail -f /path/to/terminal-mcp/logs/audit.log
```

### 常见问题

1. **路径错误**: 确保所有路径都是绝对路径且存在
2. **Python 路径**: Windows 用户需要使用完整的 python.exe 路径
3. **权限问题**: 确保对 terminal-mcp 目录有读取和执行权限
4. **编码问题**: 配置中已包含 `PYTHONIOENCODING=utf-8` 环境变量

## 安全提示

⚠️ **重要**: 此工具允许执行系统命令，请确保：

1. 仔细审查 `config/config.yaml` 中的安全设置
2. 不要在生产环境禁用命令过滤
3. 限制可访问的目录范围
4. 定期查看审计日志

详细安全配置请参考 `config/config.yaml` 和 `CLIENT_CONFIG.md`。

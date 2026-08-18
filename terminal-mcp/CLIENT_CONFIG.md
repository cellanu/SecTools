# MCP Client 配置完整指南

本文档提供各大主流 MCP Client 的详细配置步骤，包括 **ChatGPT Desktop**、**Qwen Chat**、Claude Desktop、Cursor、Continue 等。

---

## 目录

1. [前置准备](#前置准备)
2. [ChatGPT Desktop 配置](#chatgpt-desktop-配置)
3. [Qwen Chat (通义千问) 配置](#qwen-chat-通义千问-配置)
4. [Claude Desktop 配置](#claude-desktop-配置)
5. [Cursor 配置](#cursor-配置)
6. [Continue 配置](#continue-配置)
7. [其他 Client 配置](#其他-client-配置)
8. [故障排除](#故障排除)

---

## 前置准备

### 1. 安装 Terminal MCP Server

```bash
cd /path/to/terminal-mcp
pip install -r requirements.txt
```

### 2. 验证安装

```bash
python -c "import mcp; print('MCP SDK version:', mcp.__version__)"
```

### 3. 获取绝对路径

```bash
# Linux/macOS
pwd
which python

# Windows PowerShell
Get-Location
Get-Command python | Select-Object -ExpandProperty Source
```

**记录以下路径：**
- Terminal MCP Server 目录：`/path/to/terminal-mcp`
- Python 可执行文件路径：`/usr/bin/python3` 或 `C:\Python311\python.exe`
- server.py 完整路径：`/path/to/terminal-mcp/server.py`

---

## ChatGPT Desktop 配置

### 方式一：通过设置界面配置（推荐）

1. **打开 ChatGPT Desktop 应用**
   - 确保已安装最新版本（支持 MCP 的版本）

2. **进入设置**
   - 点击左下角齿轮图标 ⚙️
   - 选择 "Settings"

3. **找到 MCP 配置**
   - 导航到 "Experimental" 或 "Developer" 选项卡
   - 找到 "Model Context Protocol" 或 "MCP Servers" 部分

4. **添加服务器**
   - 点击 "Add Server" 或 "+"
   - 填写以下信息：

   ```
   Server Name: terminal
   Command: python
   Arguments: /absolute/path/to/terminal-mcp/server.py
   Working Directory: /absolute/path/to/terminal-mcp
   ```

5. **保存并重启**
   - 点击 "Save"
   - 重启 ChatGPT Desktop

### 方式二：通过配置文件配置

1. **找到配置文件位置**

   **macOS:**
   ```
   ~/Library/Application Support/ChatGPT/mcp_config.json
   ```

   **Windows:**
   ```
   %APPDATA%\ChatGPT\mcp_config.json
   ```

   **Linux:**
   ```
   ~/.config/ChatGPT/mcp_config.json
   ```

2. **编辑配置文件**

   ```json
   {
     "mcpServers": {
       "terminal": {
         "command": "python",
         "args": ["/absolute/path/to/terminal-mcp/server.py"],
         "cwd": "/absolute/path/to/terminal-mcp",
         "env": {}
       }
     }
   }
   ```

3. **替换路径占位符**

   **macOS/Linux 示例:**
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

   **Windows 示例:**
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

4. **重启 ChatGPT Desktop**

### 验证连接

1. 在 ChatGPT 对话框中输入：
   ```
   列出当前目录的文件
   ```

2. 如果配置正确，ChatGPT 会调用 `execute_command` 工具执行 `ls` 或 `dir` 命令

3. 查看日志确认：
   ```bash
   cat /path/to/terminal-mcp/logs/audit.log
   ```

---

## Qwen Chat (通义千问) 配置

### 方式一：通义千问桌面版配置

1. **打开通义千问桌面应用**
   - 确保已安装最新版本

2. **进入开发者设置**
   - 点击头像 → "设置"
   - 找到 "高级功能" 或 "开发者选项"

3. **配置 MCP Server**
   - 找到 "MCP 服务" 或 "外部工具" 选项
   - 点击 "添加服务"

4. **填写配置信息**

   ```yaml
   服务名称：terminal
   服务类型：stdio
   启动命令：python
   参数：/absolute/path/to/terminal-mcp/server.py
   工作目录：/absolute/path/to/terminal-mcp
   ```

5. **保存配置**

### 方式二：通过配置文件

1. **找到配置文件**

   **macOS:**
   ```
   ~/Library/Application Support/QwenChat/config.json
   ```

   **Windows:**
   ```
   %APPDATA%\QwenChat\config.json
   ```

   **Linux:**
   ```
   ~/.config/QwenChat/config.json
   ```

2. **添加 MCP 配置**

   ```json
   {
     "mcp": {
       "enabled": true,
       "servers": {
         "terminal": {
           "type": "stdio",
           "command": "python",
           "args": ["/absolute/path/to/terminal-mcp/server.py"],
           "cwd": "/absolute/path/to/terminal-mcp",
           "timeout": 30,
           "env": {
             "PYTHONIOENCODING": "utf-8"
           }
         }
       }
     }
   }
   ```

3. **重启通义千问**

### 方式三：Web 版配置（如支持）

如果使用 Web 版本且支持本地 MCP：

1. 安装浏览器扩展（如官方提供）
2. 在扩展设置中添加 MCP Server
3. 配置与桌面版相同

### 验证配置

在 Qwen Chat 中尝试：
```
帮我查看当前目录下有哪些文件
```

---

## Claude Desktop 配置

### macOS

1. **创建/编辑配置文件**

   ```bash
   mkdir -p ~/Library/Application\ Support/Claude
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **添加配置**

   ```json
   {
     "mcpServers": {
       "terminal": {
         "command": "python3",
         "args": ["/Users/your-username/projects/terminal-mcp/server.py"],
         "cwd": "/Users/your-username/projects/terminal-mcp"
       }
     }
   }
   ```

### Windows

1. **打开配置文件**

   按 `Win + R`，输入：
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **添加配置**

   ```json
   {
     "mcpServers": {
       "terminal": {
         "command": "C:\\Python311\\python.exe",
         "args": ["C:\\Users\\YourUsername\\projects\\terminal-mcp\\server.py"],
         "cwd": "C:\\Users\\YourUsername\\projects\\terminal-mcp"
       }
     }
   }
   ```

### Linux

1. **创建配置文件**

   ```bash
   mkdir -p ~/.config/claude
   nano ~/.config/claude/claude_desktop_config.json
   ```

2. **添加配置**

   ```json
   {
     "mcpServers": {
       "terminal": {
         "command": "python3",
         "args": ["/home/username/projects/terminal-mcp/server.py"],
         "cwd": "/home/username/projects/terminal-mcp"
       }
     }
   }
   ```

---

## Cursor 配置

### 方式一：通过设置界面

1. **打开 Cursor 设置**
   - `Cmd + ,` (macOS) 或 `Ctrl + ,` (Windows/Linux)

2. **找到 MCP 配置**
   - 导航到 "Features" → "MCP Servers"

3. **添加服务器**
   - 点击 "Add New Server"
   - 填写：
     ```
     Name: terminal
     Type: stdio
     Command: python
     Args: /path/to/terminal-mcp/server.py
     CWD: /path/to/terminal-mcp
     ```

### 方式二：通过配置文件

1. **编辑 settings.json**

   `Cmd + Shift + P` → 输入 "Open Settings (JSON)"

2. **添加配置**

   ```json
   {
     "cursor.mcp.servers": {
       "terminal": {
         "command": "python",
         "args": ["/absolute/path/to/terminal-mcp/server.py"],
         "cwd": "/absolute/path/to/terminal-mcp"
       }
     }
   }
   ```

---

## Continue 配置

### 方式一：通过 config.json

1. **打开 Continue 配置**
   - 在 VS Code 中按 `Cmd/Ctrl + Shift + P`
   - 输入 "Continue: Open Config"

2. **添加 MCP Server**

   ```json
   {
     "mcpServers": [
       {
         "name": "terminal",
         "command": "python",
         "args": ["/absolute/path/to/terminal-mcp/server.py"],
         "cwd": "/absolute/path/to/terminal-mcp"
       }
     ]
   }
   ```

### 方式二：通过 .continue 目录

在项目根目录创建 `.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "terminal",
      "command": "python3",
      "args": ["/path/to/terminal-mcp/server.py"],
      "cwd": "/path/to/terminal-mcp"
    }
  ]
}
```

---

## 其他 Client 配置

### Windsurf

```json
{
  "mcp": {
    "servers": {
      "terminal": {
        "command": "python",
        "args": ["/path/to/server.py"],
        "cwd": "/path/to/terminal-mcp"
      }
    }
  }
}
```

### Zed

在 `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "terminal": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

### Cline (VS Code 扩展)

在扩展设置中添加 MCP Server 配置，格式同上。

---

## 通用配置模板

复制并根据你的系统修改：

### macOS/Linux Template

```json
{
  "mcpServers": {
    "terminal": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/projects/terminal-mcp/server.py"],
      "cwd": "/Users/YOUR_USERNAME/projects/terminal-mcp",
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Windows Template

```json
{
  "mcpServers": {
    "terminal": {
      "command": "C:\\Python311\\python.exe",
      "args": ["C:\\Users\\YOUR_USERNAME\\projects\\terminal-mcp\\server.py"],
      "cwd": "C:\\Users\\YOUR_USERNAME\\projects\\terminal-mcp",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

---

## 故障排除

### 问题 1: Client 无法连接到 MCP Server

**症状**: Client 显示 "Failed to connect to MCP server"

**解决方案**:
1. 检查 Python 路径是否正确
   ```bash
   which python3  # macOS/Linux
   where python   # Windows
   ```

2. 检查 server.py 路径是否存在
   ```bash
   ls -la /path/to/terminal-mcp/server.py
   ```

3. 手动测试 server.py
   ```bash
   cd /path/to/terminal-mcp
   echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | python server.py
   ```

4. 检查权限
   ```bash
   chmod +x /path/to/terminal-mcp/server.py
   ```

### 问题 2: 命令执行被阻止

**症状**: 返回 "Command blocked by security filter"

**解决方案**:
1. 查看审计日志
   ```bash
   tail -f /path/to/terminal-mcp/logs/audit.log
   ```

2. 调整 config/config.yaml
   ```yaml
   security:
     allow_commands:
       - python
       - git
       - ls
       - dir
   ```

3. 临时禁用过滤器（仅测试用）
   ```yaml
   security:
     enable_command_filter: false
   ```

### 问题 3: 中文输出乱码

**解决方案**:
1. 在配置中添加环境变量
   ```json
   {
     "env": {
       "PYTHONIOENCODING": "utf-8",
       "LANG": "zh_CN.UTF-8"
     }
   }
   ```

2. 检查终端编码设置

### 问题 4: ChatGPT/Qwen 不显示工具选项

**可能原因**:
1. Client 版本过旧，不支持 MCP
2. MCP Server 未正确注册
3. 配置文件语法错误

**解决方案**:
1. 更新 Client 到最新版本
2. 重启 Client 应用
3. 使用 JSON 验证器检查配置文件
4. 查看 Client 日志

### 问题 5: 超时问题

**症状**: 长时间运行的命令被终止

**解决方案**:
1. 增加 timeout 参数
   ```json
   {
     "mcpServers": {
       "terminal": {
         "command": "python",
         "args": ["/path/to/server.py"],
         "cwd": "/path/to/terminal-mcp",
         "timeout": 300
       }
     }
   }
   ```

2. 调整 config.yaml
   ```yaml
   security:
     max_timeout: 600
     default_timeout: 60
   ```

---

## 安全建议

⚠️ **重要提醒**:

1. **不要在生产环境禁用安全过滤**
   ```yaml
   # ❌ 危险配置
   enable_command_filter: false
   
   # ✅ 安全配置
   enable_command_filter: true
   allow_commands:
     - ls
     - pwd
     - git
   ```

2. **限制可访问目录**
   ```yaml
   security:
     allowed_directories:
       - /home/username/projects
       - /tmp
     forbidden_directories:
       - /etc
       - /root
       - /boot
   ```

3. **定期审查审计日志**
   ```bash
   # 查看最近的命令执行记录
   tail -100 logs/audit.log
   
   # 查找失败的命令
   grep "STATUS: FAILED" logs/audit.log
   ```

4. **使用最小权限原则**
   - 不要以 root/Administrator 运行
   - 只开放必要的命令
   - 限制工作目录范围

---

## 快速测试命令

配置完成后，在各 Client 中尝试以下命令测试：

```
# 基础测试
列出当前目录的文件

# Git 测试（如果在 git 仓库中）
显示当前的 git 状态

# 系统信息
显示当前系统信息

# Python 测试
运行 python --version
```

如果一切正常，你应该能看到命令执行结果！

---

## 参考链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Terminal MCP Server GitHub](https://github.com/your-repo/terminal-mcp)
- [Anthropic MCP 集成指南](https://docs.anthropic.com/en/docs/build-with-claude/mcp)

# MCP Client Configurations

This directory contains ready-to-use MCP client configurations for various tools.

## Configuration Files

| Client | File | Transport | Endpoint |
|--------|------|----------|----------|
| Claude Desktop | claude-desktop.json | STDIO | local |
| Cursor | cursor.json | STDIO | local |
| Zed | zed.json | STDIO | local |
| Windsurf | windsurf.json | STDIO | local |
| VS Code (Cline) | vscode-cline.json | STDIO | local |
| LM Studio | lm-studio.json | Streamable HTTP | http://localhost:8000/mcp |
| Remote HTTP | http-remote.json | Streamable HTTP | http://localhost:8000/mcp |

## Usage

Copy the relevant JSON file to your client's configuration location:

- Claude Desktop: `~/.config/Claude/claude_desktop_config.json`
- Cursor: `~/.cursor/mcp.json`
- Zed: `~/.config/zed/settings.json`
- Windsurf: `~/.config/Windsurf/settings.json`
- LM Studio: Settings → MCP Servers

## Server Endpoints

- **STDIO mode**: Run `python -m src.server` locally
- **HTTP mode**: Run `python -m src.server http` (exposes http://localhost:8000/mcp)
# MCP Configs - Web Search & Fetch

Este servidor roda no **Docker** e expõe endpoints Streamable HTTP para clientes MCP.

## Arquitetura

```
┌─────────────────┐      ┌──────────────────────┐
│   MCP Clients    │ ──► │ Docker Container    │
│ (Zed, LM Studio,│     │ :8000 (HTTP)        │
│  Claude, etc.) │     │                   │
└─────────────────┘     └──────────────────────┘
                                │
                         ┌───────┴───────┐
                         │ searxng:8080  │
                         └──────────────┘
```

## Quick Start

```bash
# Iniciar container
docker compose up -d

# URL do servidor (Streamable HTTP)
http://localhost:8000/mcp
```

## Configuração por Cliente

### LM Studio

Abra **LM Studio** → Settings → MCP Servers → Add:

```json
{
  "mcpServers": {
    "web-search": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Claude Desktop

**Linux:**
```bash
mkdir -p ~/.config/Claude
```

Edite `~/.config/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "web-search": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**macOS:**
```bash
mkdir -p ~/Library/Application\ Support/Claude
```

**Windows:**
```cmd
%APPDATA%\Claude\claude_desktop_config.json
```

### Cursor

**Linux/macOS:**
```bash
mkdir -p ~/.cursor
```

Edite `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "web-search": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Windows:**
```cmd
%APPDATA%\Cursor\User\settings.json
```

### Zed

Edite `~/.config/zed/settings.json`:
```json
{
  "context_servers": {
    "web-search": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Windsurf

**Linux:**
```bash
mkdir -p ~/.config/Windsurf
```

Edite `~/.config/Windsurf/settings.json`:
```json
{
  "mcpServers": {
    "web-search": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Windows:**
```cmd
%APPDATA%\Windsurf\User\settings.json
```

### VS Code (Cline)

Edite `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`:
```json
{
  "mcpServers": {
    "web-search": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Acesso Remoto

Para acessar de outro computador, substitua `localhost` pelo IP do host:

```json
{
  "mcpServers": {
    "web-search": {
      "url": "http://192.168.1.100:8000/mcp"
    }
  }
}
```

## Variáveis de Ambiente

No `docker-compose.yml`, adicione:
```yaml
environment:
  - SEARXNG_HOST=http://searxng:8080
  - API_KEY=sua-chave-aqui
```

## Porta customizada

Para mudar a porta (ex: 8090):

```yaml
# docker-compose.yml
ports:
  - "8090:8000"

# Configuração do cliente
"url": "http://localhost:8090/mcp"
```

## Troubleshooting

### "Connection refused"
- Verifique se o container está rodando: `docker ps`
- Verifique logs: `docker logs lm-studio-mcp-server`

### "Timeout"
- Use a URL `/mcp` (Streamable HTTP), não `/sse`

### "Invalid params"
- Verifique se a URL está correta: deve terminar em `/mcp`
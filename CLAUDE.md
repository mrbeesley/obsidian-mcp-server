# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An MCP server and CLI that connects AI agents to Obsidian vaults via the Obsidian Local REST API plugin. Built with Python and FastMCP.

## Build & Run

```bash
uv sync                        # Install dependencies
uv run obsidian-mcp            # Run the MCP server (stdio transport)
uv run fastmcp dev src/obsidian_mcp/server.py  # Dev inspector UI
```

## Architecture

- `src/obsidian_mcp/server.py` — FastMCP server with tool definitions (`create_note`, `search_notes`, `read_note`)
- `src/obsidian_mcp/client.py` — Async HTTP client (`ObsidianClient`) wrapping Obsidian Local REST API calls via httpx

The server acts as a bridge: MCP clients (like Claude) call tools, which translate to HTTP requests against the Obsidian Local REST API running locally.

## Configuration

Environment variables:
- `OBSIDIAN_API_URL` — Base URL (default: `https://127.0.0.1:27124`)
- `OBSIDIAN_API_KEY` — Bearer token for authentication

SSL verification is disabled since Obsidian Local REST API uses self-signed certs.

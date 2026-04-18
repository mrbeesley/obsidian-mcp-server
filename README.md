# Obsidian MCP Server

An MCP (Model Context Protocol) server that connects AI assistants like Claude to your Obsidian vault. It uses the [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin to search, read, and create notes — giving AI agents full context from your knowledge base.

Built with [FastMCP](https://github.com/jlowin/fastmcp) and Python.

## Prerequisites

- [Obsidian](https://obsidian.md/) with the **Local REST API** plugin installed and enabled
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.10+

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/obsidian-mcp-server.git
   cd obsidian-mcp-server
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Configure environment variables:**

   Create a `.env` file in the project root:

   ```
   OBSIDIAN_API_KEY=your-api-key-here
   ```

   Find your API key in Obsidian under **Settings > Local REST API**.

   | Variable | Description | Default |
   |---|---|---|
   | `OBSIDIAN_API_KEY` | Bearer token for authenticating with the Obsidian REST API | *(required)* |
   | `OBSIDIAN_API_URL` | Base URL of the Obsidian Local REST API | `https://127.0.0.1:27124` |

4. **Start Obsidian** and ensure the Local REST API plugin is running.

## Running the Server

```bash
uv run obsidian-mcp
```

This starts the MCP server using stdio transport, ready to accept connections from an MCP client.

### Development Mode

Use the FastMCP inspector to test tools interactively in a browser UI:

```bash
uv run fastmcp dev src/obsidian_mcp/server.py
```

## Connecting to Claude Desktop

Add the following to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uv",
      "args": ["--directory", "/path/to/obsidian-mcp-server", "run", "obsidian-mcp"],
      "env": {
        "OBSIDIAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Replace `/path/to/obsidian-mcp-server` with the absolute path to your cloned repository, and set your API key. Restart Claude Desktop after saving.

## Tools

The server exposes eleven tools that AI agents can call:

### `create_note`

Creates a new note in the vault.

| Parameter | Type | Description |
|---|---|---|
| `filename` | `str` | Path for the new note relative to vault root (e.g. `"folder/note.md"`) |
| `content` | `str` | Markdown content for the note |

### `search_notes`

Performs a full-text search across all notes in the vault using Obsidian's native search.

| Parameter | Type | Description |
|---|---|---|
| `query` | `str` | The search query string |

Returns matching filenames with text snippets from the results.

### `read_note`

Reads the full markdown content of a specific note.

| Parameter | Type | Description |
|---|---|---|
| `path` | `str` | Path to the note relative to vault root (e.g. `"folder/note.md"`) |

### `update_note`

Updates an existing note. When called without targeting parameters, it appends content to the end of the note. When called with `target_type` and `target`, it performs a targeted update on a specific section.

| Parameter | Type | Description |
|---|---|---|
| `path` | `str` | Path to the note relative to vault root (e.g. `"folder/note.md"`) |
| `content` | `str` | Markdown content to write |
| `target_type` | `str` *(optional)* | Type of target: `"heading"`, `"block"`, or `"frontmatter"` |
| `target` | `str` *(optional)* | The specific heading name or block ID (e.g. `"My Heading"`) |
| `operation` | `str` *(optional)* | How to apply the update: `"replace"`, `"append"`, or `"prepend"`. Defaults to `"replace"` |

**Examples:**
- **Append to a note:** Call with just `path` and `content` — content is added to the end.
- **Replace a heading section:** Set `target_type="heading"`, `target="My Heading"`, `operation="replace"`.
- **Prepend to a block:** Set `target_type="block"`, `target="block-id"`, `operation="prepend"`.

### `list_tags`

Returns all tags in the vault with their usage counts. Useful for discovering what tags exist before searching by tag.

*No parameters.*

### `list_commands`

Returns all available Obsidian commands (built-in and plugin-provided) with their IDs. Call this before `execute_command` to discover available commands.

*No parameters.*

### `execute_command`

Executes an Obsidian command by its ID. Use `list_commands` first to discover available commands.

| Parameter | Type | Description |
|---|---|---|
| `command_id` | `str` | The command ID to execute (e.g. `"editor:toggle-checklist-status"`) |

### `open_note`

Opens a note in the Obsidian UI so the user can see it directly.

| Parameter | Type | Description |
|---|---|---|
| `path` | `str` | Path to the note relative to vault root (e.g. `"folder/note.md"`) |

### `list_notes`

Lists notes in a folder or the entire vault. Complements `search_notes` — search finds notes by content, this finds notes by location.

| Parameter | Type | Description |
|---|---|---|
| `folder` | `str` *(optional)* | Folder path relative to vault root (e.g. `"Projects"`). Empty for entire vault |

### `get_daily_note`

Reads today's daily note or a daily note for a specific date. Avoids needing to guess daily note naming conventions or folder structure.

| Parameter | Type | Description |
|---|---|---|
| `date` | `str` *(optional)* | Date in `YYYY-MM-DD` format. If not provided, returns today's daily note |

### `find_backlinks`

Finds all notes that link to the given note using `[[wiki-link]]` syntax. Surfaces relationship context by finding notes that explicitly reference the target note through Obsidian's linking system.

| Parameter | Type | Description |
|---|---|---|
| `path` | `str` | Path to the note relative to vault root (e.g. `"folder/note.md"`) |

### `get_recent_notes`

Returns notes modified within a given time window, sorted by most recent first. Uses file listing metadata to find recently modified notes.

| Parameter | Type | Description |
|---|---|---|
| `days` | `int` *(optional)* | Number of days to look back (default: `7`) |

## Prompts

### `weekly_review`

A built-in prompt that instructs the AI to perform a weekly review of your vault. It searches for recent notes, categorizes them (completed work, in progress, new ideas, action items), and produces a digest summary. Optionally specify the number of days to look back (default: 7).

### `summarize_topic`

Searches the vault for all notes related to a given topic and produces a consolidated summary organized by theme. It uses multiple search queries (including synonyms and variations) to find relevant notes, then synthesizes the findings into an overview with key insights, open questions, and related topics.

| Parameter | Type | Description |
|---|---|---|
| `topic` | `str` | The topic to search for and summarize across your vault |

## Architecture

```
src/obsidian_mcp/
├── server.py    # FastMCP server — defines tools and prompts
└── client.py    # ObsidianClient — async HTTP client wrapping the Obsidian REST API
```

The server acts as a bridge between MCP clients and Obsidian. When an AI agent calls a tool, the server translates it into an HTTP request against the Obsidian Local REST API running on your machine.

**Note:** SSL verification is disabled by default because the Obsidian Local REST API uses self-signed certificates.

## License

MIT

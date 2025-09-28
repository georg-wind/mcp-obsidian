# MCP server for Obsidian

MCP server providing 25 tools to interact with Obsidian via the Local REST API community plugin, including active note operations, periodic notes management, and command execution.

<a href="https://glama.ai/mcp/servers/3wko1bhuek"><img width="380" height="200" src="https://glama.ai/mcp/servers/3wko1bhuek/badge" alt="server for Obsidian MCP server" /></a>

## Components

### Tools

The server implements 25 tools to interact with Obsidian, organized by functionality:

#### File & Content Operations
- obsidian_list_files_in_vault: Lists all files and directories in the root directory of your Obsidian vault
- obsidian_list_files_in_dir: Lists all files and directories in a specific Obsidian directory
- obsidian_get_file_contents: Return the content of a single file in your vault
- obsidian_batch_get_file_contents: Return the contents of multiple files in your vault, concatenated with headers
- obsidian_simple_search: Search for documents matching a specified text query across all files in the vault
- obsidian_complex_search: Complex search for documents using JsonLogic queries with glob and regexp support
- obsidian_patch_content: Insert content into an existing note relative to a heading, block reference, or frontmatter field
- obsidian_append_content: Append content to a new or existing file in the vault
- obsidian_put_content: Create a new file or update the content of an existing file in your vault
- obsidian_delete_file: Delete a file or directory from your vault

#### Active Note Operations
- obsidian_get_active: Get content of the currently active note in Obsidian
- obsidian_post_active: Append content to the currently active note
- obsidian_put_active: Replace entire content of the currently active note
- obsidian_patch_active: Insert/replace content in active note relative to a heading, block reference, or frontmatter field
- obsidian_delete_active: Delete the currently active note

#### Periodic Notes Management
- obsidian_get_periodic_note: Get current periodic note for specified period (daily/weekly/monthly/quarterly/yearly)
- obsidian_post_periodic: Append content to the current periodic note
- obsidian_put_periodic: Replace entire content of the current periodic note
- obsidian_patch_periodic: Insert/replace content in periodic note relative to a heading, block reference, or frontmatter field
- obsidian_delete_periodic: Delete the current periodic note

#### Commands & UI Control
- obsidian_get_commands: List all available Obsidian commands from the command palette
- obsidian_execute_command: Execute a specific Obsidian command by its ID
- obsidian_open_file: Open a file in Obsidian UI, optionally in a new tab/pane

#### Advanced Features
- obsidian_get_recent_periodic_notes: Get most recent periodic notes for specified period type
- obsidian_get_recent_changes: Get recently modified files in the vault

### Example prompts

It's good to first instruct Claude to use Obsidian. Then it will always call the tool.

#### File & Search Operations
- Get the contents of the last architecture call note and summarize them
- Search for all files where Azure CosmosDb is mentioned and quickly explain to me the context in which it is mentioned
- Summarize the last meeting notes and put them into a new note 'summary meeting.md'. Add an introduction so that I can send it via email
- Find all notes containing project deadlines and create a consolidated timeline

#### Active Note Operations  
- Add this meeting summary to the note I currently have open
- Replace the active note content with the updated version I'm about to provide
- Insert a new "Action Items" section under the "Meeting Notes" heading in my active document
- Append today's accomplishments to whatever note I have open right now

#### Periodic Notes Management
- Add today's tasks to my daily note
- Get the content of this week's weekly note and summarize the key points
- Create a monthly review section in my monthly periodic note with this quarter's achievements
- Append my standup update to today's daily note
- Show me what's in my quarterly note and help me plan the next quarter

#### Command Execution & UI Control
- Open my project notes in a new tab so I can reference them
- Execute the 'Toggle Reading View' command to switch the current view
- Show me all available Obsidian commands so I can see what's possible
- Open the file 'Projects/2024/planning.md' in a new pane
- Run the command to create a new note from my meeting template

## Path Encoding & Filename Support

The server includes robust path encoding that handles filenames with spaces, special characters, Unicode, and emojis. All file operations work seamlessly with complex filenames.

### Supported Filename Types

- **Spaces**: `Projects/2024 Q1/meeting notes.md`
- **Unicode characters**: `Área/configuração/São Paulo.md`  
- **Special characters**: `Research (2024)/data #1 & analysis + results.md`
- **Emojis**: `Projects 🚀/📘 documentation/notes ⭐.md`
- **Mixed types**: `Área (Special) & More + [Data] = Value #1 🚀.md`

### Technical Features

- **Idempotent**: Prevents double-encoding of already encoded paths
- **Unicode normalization**: Normalizes to NFC for cross-platform consistency
- **RFC 3986 compliant**: Preserves safe characters (-_.~) while encoding others  
- **Directory structure preservation**: Maintains "/" separators and trailing "/" slashes
- **Backward compatible**: No changes to existing simple filename behavior

### Example Operations

```python
# All these filename types work with any operation:
obsidian_get_file_contents("Projects/Meeting Notes 📝.md")
obsidian_append_content("Área/configuração.md", "New content")
obsidian_list_files_in_dir("Special (Folder) & More")
obsidian_patch_content("Research #1/data + analysis.md", ...)
obsidian_list_files_in_dir("Reports/2024/")
```

## Configuration

### Environment Variables

The MCP server requires the following environment variables:

- `OBSIDIAN_API_KEY`: Your Obsidian Local REST API key (required)
- `OBSIDIAN_HOST`: The URL for your Obsidian Local REST API (optional, defaults to `https://127.0.0.1:27124`)

#### OBSIDIAN_HOST Format

The `OBSIDIAN_HOST` variable accepts full URLs with protocol, host, and port. It supports both `localhost` and `127.0.0.1` with either `http` or `https`:

```
http://127.0.0.1:27123
https://localhost:27124
http://localhost:27123
https://127.0.0.1:27124
```

**Note:** The server performs a health check on startup. If the connection fails, you'll get an immediate error message indicating the configuration issue.

### Configuration Methods

There are two ways to configure the environment variables:

#### 1. Add to server config (preferred)

```json
{
  "mcp-obsidian": {
    "command": "uvx",
    "args": [
      "mcp-obsidian"
    ],
    "env": {
      "OBSIDIAN_API_KEY": "<your_api_key_here>",
      "OBSIDIAN_HOST": "<your_obsidian_host>"
    }
  }
}
```

#### 2. Create a `.env` file in the working directory with the following required variable:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=your_obsidian_host
```

**Note:** You can find the API key in the Obsidian Local REST API plugin configuration.

## Quickstart

### Install

#### Obsidian REST API

You need the Obsidian REST API community plugin running: https://github.com/coddingtonbear/obsidian-local-rest-api

Install and enable it in the settings and copy the api key.

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "<dir_to>/mcp-obsidian",
        "run",
        "mcp-obsidian"
      ]
    }
  }
}
```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": [
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "<your_obsidian_host>"
      }
    }
  }
}
```
</details>

## Development

### Building

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-obsidian run mcp-obsidian
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

You can also watch the server logs with this command:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-mcp-obsidian.log
```

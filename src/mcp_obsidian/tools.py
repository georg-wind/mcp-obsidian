import json
import os
from typing import Sequence

from mcp.server import FastMCP
from mcp.types import TextContent

from mcp_obsidian import obsidian

# Validate environment
api_key = os.getenv("OBSIDIAN_API_KEY")
if not api_key:
    raise ValueError("OBSIDIAN_API_KEY environment variable required")

obsidian_host = os.getenv("OBSIDIAN_HOST", "https://127.0.0.1:27124")
protocol, host, port = obsidian.Obsidian.parse_host_config(obsidian_host)


def get_api():
    """Get configured Obsidian API instance."""
    return obsidian.Obsidian(
        api_key=api_key,
        protocol=protocol,
        host=host,
        port=port,
        verify_ssl=False
    )


def init_tools(mcp: FastMCP):
    @mcp.tool()
    def obsidian_list_files_in_vault() -> Sequence[TextContent]:
        """Lists all files and directories in the root directory of your Obsidian vault."""
        api = get_api()
        files = api.list_files_in_vault()
        return [TextContent(type="text", text=json.dumps(files, indent=2))]

    @mcp.tool()
    def obsidian_list_files_in_dir(dirpath: str) -> Sequence[TextContent]:
        """Lists all files and directories in a specific Obsidian directory.

        Args:
            dirpath: Path to list files from (relative to vault root). Empty directories won't be returned.
        """
        api = get_api()
        files = api.list_files_in_dir(dirpath)
        return [TextContent(type="text", text=json.dumps(files, indent=2))]

    @mcp.tool()
    def obsidian_get_file_contents(filepath: str) -> Sequence[TextContent]:
        """Return the content of a single file in your vault.

        Args:
            filepath: Path to the file (relative to vault root)
        """
        api = get_api()
        content = api.get_file_contents(filepath)
        return [TextContent(type="text", text=json.dumps(content, indent=2))]

    @mcp.tool()
    def obsidian_simple_search(query: str, context_length: int = 100) -> Sequence[TextContent]:
        """Simple search for documents matching text query across all files.

        Args:
            query: Text to search for in the vault
            context_length: How much context to return around matches (default: 100)
        """
        api = get_api()
        results = api.search(query, context_length)

        formatted_results = []
        for result in results:
            formatted_matches = [{
                'context': match.get('context', ''),
                'match_position': {
                    'start': match['match']['start'],
                    'end': match['match']['end']
                }
            } for match in result.get('matches', [])]

            formatted_results.append({
                'filename': result.get('filename', ''),
                'score': result.get('score', 0),
                'matches': formatted_matches
            })

        return [TextContent(type="text", text=json.dumps(formatted_results, indent=2))]

    @mcp.tool()
    def obsidian_append_content(filepath: str, content: str) -> Sequence[TextContent]:
        """Append content to a new or existing file in the vault.

        Args:
            filepath: Path to the file (relative to vault root)
            content: Content to append to the file
        """
        api = get_api()
        api.append_content(filepath, content)
        return [TextContent(type="text", text=f"Successfully appended content to {filepath}")]

    @mcp.tool()
    def obsidian_patch_content(
            filepath: str,
            operation: str,
            target_type: str,
            target: str,
            content: str
    ) -> Sequence[TextContent]:
        """Insert content into an existing note relative to a heading, block reference, or frontmatter field.

        Args:
            filepath: Path to the file (relative to vault root)
            operation: Operation to perform (append, prepend, or replace)
            target_type: Type of target to patch (heading, block, or frontmatter)
            target: Target identifier (heading path, block reference, or frontmatter field)
            content: Content to insert
        """
        api = get_api()
        api.patch_content(filepath, operation, target_type, target, content)
        return [TextContent(type="text", text=f"Successfully patched content in {filepath}")]

    @mcp.tool()
    def obsidian_put_content(filepath: str, content: str) -> Sequence[TextContent]:
        """Create a new file or update content of an existing file.

        Args:
            filepath: Path to the file (relative to vault root)
            content: Content of the file
        """
        api = get_api()
        api.put_content(filepath, content)
        return [TextContent(type="text", text=f"Successfully uploaded content to {filepath}")]

    @mcp.tool()
    def obsidian_delete_file(filepath: str, confirm: bool) -> Sequence[TextContent]:
        """Delete a file or directory from the vault.

        Args:
            filepath: Path to the file or directory to delete (relative to vault root)
            confirm: Confirmation to delete (must be true)
        """
        if not confirm:
            raise RuntimeError("confirm must be set to true to delete a file")

        api = get_api()
        api.delete_file(filepath)
        return [TextContent(type="text", text=f"Successfully deleted {filepath}")]

    @mcp.tool()
    def obsidian_complex_search(query: dict) -> Sequence[TextContent]:
        """Complex search for documents using a JsonLogic query.

        Supports standard JsonLogic operators plus 'glob' and 'regexp' for pattern matching.

        Examples:
        - Match all markdown files: {"glob": ["*.md", {"var": "path"}]}
        - Match markdown files with substring: {"and": [{"glob": ["*.md", {"var": "path"}]}, {"regexp": [".*1221.*", {"var": "content"}]}]}
        - Match in specific folder: {"and": [{"glob": ["*.md", {"var": "path"}]}, {"regexp": [".*Work.*", {"var": "path"}]}, {"regexp": ["Keaton", {"var": "content"}]}]}

        Args:
            query: JsonLogic query object
        """
        api = get_api()
        results = api.search_json(query)
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    @mcp.tool()
    def obsidian_batch_get_file_contents(filepaths: list[str]) -> Sequence[TextContent]:
        """Return the contents of multiple files in your vault, concatenated with headers.

        Args:
            filepaths: List of file paths to read (relative to vault root)
        """
        api = get_api()
        content = api.get_batch_file_contents(filepaths)
        return [TextContent(type="text", text=content)]

    @mcp.tool()
    def obsidian_get_periodic_note(period: str, as_json: bool = False) -> Sequence[TextContent]:
        """Get current periodic note for the specified period.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            as_json: Whether to return JSON format with metadata (default: false)
        """
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise RuntimeError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")

        api = get_api()
        content = api.get_periodic_note(period, as_json)

        text = json.dumps(content, indent=2) if as_json else content
        return [TextContent(type="text", text=text)]

    @mcp.tool()
    def obsidian_get_recent_periodic_notes(
            period: str,
            limit: int = 5,
            include_content: bool = False
    ) -> Sequence[TextContent]:
        """Get most recent periodic notes for the specified period type.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            limit: Maximum number of notes to return (default: 5, max: 50)
            include_content: Whether to include note content (default: false)
        """
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise RuntimeError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")

        if not isinstance(limit, int) or limit < 1:
            raise RuntimeError("limit must be a positive integer")

        api = get_api()
        results = api.get_recent_periodic_notes(period, limit, include_content)
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    @mcp.tool()
    def obsidian_get_recent_changes(limit: int = 10, days: int = 90) -> Sequence[TextContent]:
        """Get recently modified files in the vault.

        Args:
            limit: Maximum number of files to return (default: 10, max: 100)
            days: Only include files modified within this many days (default: 90)
        """
        if not isinstance(limit, int) or limit < 1:
            raise RuntimeError("limit must be a positive integer")
        if not isinstance(days, int) or days < 1:
            raise RuntimeError("days must be a positive integer")

        api = get_api()
        results = api.get_recent_changes(limit, days)
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    @mcp.tool()
    def obsidian_get_active(as_json: bool = False) -> Sequence[TextContent]:
        """Get content of the currently active note in Obsidian.

        Args:
            as_json: Whether to return JSON format with metadata (default: false)
        """
        api = get_api()
        content = api.get_active_note(as_json)
        text = json.dumps(content, indent=2) if as_json else content
        return [TextContent(type="text", text=text)]

    @mcp.tool()
    def obsidian_post_active(content: str) -> Sequence[TextContent]:
        """Append content to the currently active note.

        Args:
            content: Content to append to the active note
        """
        api = get_api()
        api.append_to_active(content)
        return [TextContent(type="text", text="Successfully appended content to active note")]

    @mcp.tool()
    def obsidian_put_active(content: str) -> Sequence[TextContent]:
        """Replace entire content of the currently active note.

        Args:
            content: New content for the active note
        """
        api = get_api()
        api.replace_active_note(content)
        return [TextContent(type="text", text="Successfully replaced content of active note")]

    @mcp.tool()
    def obsidian_patch_active(
            operation: str,
            target_type: str,
            target: str,
            content: str
    ) -> Sequence[TextContent]:
        """Insert content into active note relative to a heading, block reference, or frontmatter field.

        Args:
            operation: Operation to perform (append, prepend, or replace)
            target_type: Type of target to patch (heading, block, or frontmatter)
            target: Target identifier
            content: Content to insert
        """
        api = get_api()
        api.patch_active_note(operation, target_type, target, content)
        return [TextContent(type="text", text="Successfully patched content in active note")]

    @mcp.tool()
    def obsidian_delete_active(confirm: bool) -> Sequence[TextContent]:
        """Delete the currently active note. Use with caution.

        Args:
            confirm: Confirmation to delete (must be true)
        """
        if not confirm:
            raise RuntimeError("confirm must be set to true to delete the active note")

        api = get_api()
        api.delete_active_note()
        return [TextContent(type="text", text="Successfully deleted active note")]

    @mcp.tool()
    def obsidian_post_periodic(period: str, content: str) -> Sequence[TextContent]:
        """Append content to the current periodic note.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            content: Content to append
        """
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise RuntimeError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")

        api = get_api()
        api.append_to_periodic(period, content)
        return [TextContent(type="text", text=f"Successfully appended content to {period} note")]

    @mcp.tool()
    def obsidian_put_periodic(period: str, content: str) -> Sequence[TextContent]:
        """Replace entire content of the current periodic note.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            content: New content
        """
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise RuntimeError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")

        api = get_api()
        api.replace_periodic_note(period, content)
        return [TextContent(type="text", text=f"Successfully replaced content of {period} note")]

    @mcp.tool()
    def obsidian_patch_periodic(
            period: str,
            operation: str,
            target_type: str,
            target: str,
            content: str
    ) -> Sequence[TextContent]:
        """Insert content into periodic note relative to a heading, block reference, or frontmatter field.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            operation: Operation to perform (append, prepend, or replace)
            target_type: Type of target to patch (heading, block, or frontmatter)
            target: Target identifier
            content: Content to insert
        """
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise RuntimeError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")

        api = get_api()
        api.patch_periodic_note(period, operation, target_type, target, content)
        return [TextContent(type="text", text=f"Successfully patched content in {period} note")]

    @mcp.tool()
    def obsidian_delete_periodic(period: str, confirm: bool) -> Sequence[TextContent]:
        """Delete the current periodic note. Use with caution.

        Args:
            period: The period type (daily, weekly, monthly, quarterly, yearly)
            confirm: Confirmation to delete (must be true)
        """
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise RuntimeError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")

        if not confirm:
            raise RuntimeError("confirm must be set to true to delete the periodic note")

        api = get_api()
        api.delete_periodic_note(period)
        return [TextContent(type="text", text=f"Successfully deleted {period} note")]

    @mcp.tool()
    def obsidian_get_commands() -> Sequence[TextContent]:
        """List all available Obsidian commands from the command palette."""
        api = get_api()
        commands = api.list_commands()

        commands_info = []
        if commands and "commands" in commands:
            for cmd in commands["commands"]:
                commands_info.append(f"ID: {cmd.get('id', '')} | Name: {cmd.get('name', '')}")

        result = "\n".join(commands_info) if commands_info else "(no commands available)"
        return [TextContent(type="text", text=result)]

    @mcp.tool()
    def obsidian_execute_command(command_id: str) -> Sequence[TextContent]:
        """Execute a specific Obsidian command by its ID.

        WARNING: Some commands may be destructive or change settings. Use with caution.

        Args:
            command_id: The ID of the command to execute (use obsidian_get_commands to see available IDs)
        """
        api = get_api()
        api.execute_command(command_id)
        return [TextContent(type="text", text=f"Successfully executed command: {command_id}")]

    @mcp.tool()
    def obsidian_open_file(filename: str, new_leaf: bool = False) -> Sequence[TextContent]:
        """Open a file in Obsidian UI, optionally in a new leaf (tab/pane).

        Args:
            filename: Path to the file to open (relative to vault root)
            new_leaf: If true, opens in new tab/pane; if false, opens in current view (default: false)
        """
        api = get_api()
        api.open_file(filename, new_leaf)
        return [TextContent(type="text", text=f"Successfully opened file: {filename} (new_leaf={new_leaf})")]

from fastmcp import FastMCP
from pydantic import Field

from obsidian_mcp.client import ObsidianClient

mcp = FastMCP("obsidian")
client = ObsidianClient()


@mcp.tool()
async def create_note(filename: str, content: str) -> str:
    """Create a new note in the Obsidian vault.

    Args:
        filename: Path for the new note relative to vault root (e.g. "folder/note.md").
        content: Markdown content for the note.
    """
    result = await client.create_note(filename, content)
    return f"Created note: {result['path']}"


@mcp.tool()
async def search_notes(query: str) -> str:
    """Search across all notes in the Obsidian vault using full-text search.

    Args:
        query: The search query string.
    """
    results = await client.search_notes(query)
    if not results:
        return "No results found."

    lines = []
    for item in results:
        filename = item.get("filename", "unknown")
        matches = item.get("matches", [])
        snippet = ""
        if matches:
            match = matches[0].get("match", {})
            snippet = match.get("content", "").strip()[:200]
        lines.append(f"- **{filename}**")
        if snippet:
            lines.append(f"  {snippet}")
    return "\n".join(lines)


@mcp.tool()
async def read_note(path: str) -> str:
    """Read the full content of a note from the Obsidian vault.

    Args:
        path: Path to the note relative to vault root (e.g. "folder/note.md").
    """
    return await client.read_note(path)


@mcp.tool()
async def update_note(
    path: str,
    content: str,
    target_type: str | None = None,
    target: str | None = None,
    operation: str = "replace",
) -> str:
    """Update an existing note in the Obsidian vault.

    Without target_type/target, appends content to the end of the note.
    With target_type and target, performs a targeted update on a specific section.

    Args:
        path: Path to the note relative to vault root (e.g. "folder/note.md").
        content: Markdown content to write.
        target_type: Type of target to update: "heading", "block", or "frontmatter".
        target: The specific heading name or block ID to target (e.g. "My Heading").
        operation: How to apply the update: "replace", "append", or "prepend". Defaults to "replace".
    """
    if target_type and target:
        result = await client.patch_note(path, content, target_type, target, operation)
        return f"Updated note: {result['path']} ({result['operation']} on {target_type} '{target}')"
    else:
        result = await client.append_note(path, content)
        return f"Appended to note: {result['path']}"



@mcp.prompt(
    name="weekly_review",
    description="Reviews notes from the past week and generates a digest of activity, progress, and follow-ups."
)
def weekly_review(
    days: str = Field(default="7", description="Number of days to look back (as a string, default '7').")
) -> str:
    """Generates a prompt that instructs the AI to perform a weekly review of recent Obsidian notes."""
    return f"""Please perform a weekly review of my Obsidian vault by following these steps:

1. **Search for recent activity**: Use the search_notes tool to find notes that were created or modified in the last {days} days. Try searching for common markers like dates, tags, or project names to cast a wide net.

2. **Read and categorize**: For each relevant note you find, use the read_notes tool to get its full content. Categorize each note into one of these buckets:
   - **Completed work**: Things that were finished or decisions that were made.
   - **In progress**: Work that has been started but is not yet complete.
   - **New ideas or captures**: Notes that represent new thoughts, bookmarks, or things to explore later.
   - **Action items / Follow-ups**: Any TODOs, open questions, or items that need attention.

3. **Synthesize a digest**: Produce a concise weekly review summary with these sections:
   - **Accomplishments**: What got done this week.
   - **Still In Progress**: What's actively being worked on and any blockers.
   - **New Captures**: New ideas or references that were noted down.
   - **Action Items**: A consolidated list of things that need follow-up, pulled from across all the notes.
   - **Suggested Focus for Next Week**: Based on what you found, suggest 2-3 priorities.

4. **Offer to save**: Ask me if I'd like you to create a new note in my vault with this weekly review summary.

Be thorough in your searching — try multiple queries to make sure you don't miss anything. Look for tags like #todo, #followup, #inprogress, or any project-specific tags you encounter."""


@mcp.prompt(
    name="summarize_topic",
    description="Searches the vault for all notes related to a topic and produces a consolidated summary."
)
def summarize_topic(
    topic: str = Field(description="The topic to search for and summarize across your vault.")
) -> str:
    """Generates a prompt that instructs the AI to find and summarize all notes related to a given topic."""
    return f"""Please summarize everything in my Obsidian vault related to "{topic}" by following these steps:

1. **Broad search**: Use the search_notes tool to find all notes related to "{topic}". Try multiple search queries using synonyms, related terms, and variations to make sure you capture everything relevant. For example, if the topic is "machine learning", also try "ML", "neural network", "deep learning", etc.

2. **Read and extract**: For each relevant note found, use the read_notes tool to read its full content. Extract the key points, decisions, insights, and any open questions related to "{topic}".

3. **Identify connections**: As you read through the notes, pay attention to how they relate to each other. Are there contradictions? Does one note build on another? Are there recurring themes or evolving ideas?

4. **Produce a consolidated summary** with these sections:
   - **Overview**: A high-level summary of what I know about "{topic}" based on my notes.
   - **Key Insights**: The most important points, decisions, or learnings — deduplicated and organized logically rather than note-by-note.
   - **Open Questions**: Any unresolved questions, TODOs, or areas where my notes are incomplete or contradictory.
   - **Related Topics**: Other topics or tags that came up frequently alongside "{topic}" that I might want to explore.
   - **Sources**: List the note titles/paths you pulled from so I can revisit them.

5. **Offer to save**: Ask me if I'd like you to create a new note with this summary.

Important: Organize the summary by *theme*, not by individual note. The goal is to synthesize my knowledge into a coherent picture, not just list what each note says."""

def main():
    mcp.run()


if __name__ == "__main__":
    main()

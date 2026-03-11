

import base64
import re
from datetime import UTC, datetime

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types


ROOT_PROMPT = """
You are an Artifact Notebook Assistant.

Primary behavior:
1. When asked to create/save notes, call save_note_artifact.
2. When asked to add content to an existing note, call append_to_note_artifact.
3. When asked to fetch a note, call read_note_artifact.
4. When asked what files exist, call list_note_artifacts.
5. When asked to remember user preferences for this demo, use save_user_profile_artifact.
6. When asked to recall user preferences, use read_user_profile_artifact.

Always use tools for file persistence instead of pretending a file was saved.
If a requested file is missing, call list_note_artifacts and clearly tell the user what exists.
"""


def _normalize_filename(name: str, default_suffix: str = ".md") -> str:
    """Normalize user-provided names into safe artifact filenames.

    Args:
        name: Raw name provided by user or model.
        default_suffix: Suffix to append when no extension is present.

    Returns:
        A lowercase, filesystem-safe filename.
    """
    cleaned = name.strip().lower()
    cleaned = re.sub(r"[^a-z0-9._-]+", "-", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-.")
    if not cleaned:
        cleaned = "note"
    if "." not in cleaned:
        cleaned = f"{cleaned}{default_suffix}"
    return cleaned


def _part_to_text(part: types.Part | None) -> str:
    """Convert an ADK `types.Part` payload to UTF-8 text.

    Supports both direct text parts and inline binary payloads.

    Args:
        part: Artifact content returned by `load_artifact`.

    Returns:
        Decoded text content, or empty string when unavailable.
    """
    if part is None:
        return ""

    if getattr(part, "text", None):
        return part.text

    inline_data = getattr(part, "inline_data", None)
    if inline_data and getattr(inline_data, "data", None):
        data = inline_data.data
        if isinstance(data, bytes):
            return data.decode("utf-8", errors="replace")
        try:
            return base64.b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return str(data)

    return ""


def _text_part(payload: str, mime_type: str = "text/markdown") -> types.Part:
    """Build an artifact `Part` from text bytes and MIME type.

    Args:
        payload: Text content to persist.
        mime_type: MIME type for the stored payload.

    Returns:
        A `types.Part` containing inline binary data.
    """
    return types.Part(
        inline_data=types.Blob(
            mime_type=mime_type,
            data=payload.encode("utf-8"),
        )
    )


async def save_note_artifact(note_title: str, note_body: str, tool_context: ToolContext) -> dict:
    """Create a text note and save it as an artifact.

    Args:
        note_title: Human-friendly title or file stem (for example: "rag-basics")
        note_body: Main markdown/text content to save

    Returns:
        Dict with status, filename, and new artifact version.
    """
    filename = _normalize_filename(note_title)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    payload = f"# {note_title.strip() or 'Note'}\n\n{note_body.strip()}\n\n---\nSaved at: {timestamp}\n"

    version = await tool_context.save_artifact(
        filename=filename,
        artifact=_text_part(payload, mime_type="text/markdown"),
    )

    return {
        "status": "success",
        "filename": filename,
        "version": version,
        "report": f"Saved note to {filename} (version {version}).",
    }


async def append_to_note_artifact(filename: str, additional_text: str, tool_context: ToolContext) -> dict:
    """Append text to an existing note and save as a new artifact version.

    Args:
        filename: Target artifact filename.
        additional_text: Content to append to the note.
        tool_context: ADK tool context for artifact operations.

    Returns:
        Dict with success/error status, filename, and resulting version.
    """
    normalized = _normalize_filename(filename)
    existing = await tool_context.load_artifact(filename=normalized)

    if existing is None:
        return {
            "status": "error",
            "error": "artifact_not_found",
            "report": f"Could not find artifact '{normalized}'. Use list_note_artifacts first.",
        }

    current_text = _part_to_text(existing).strip()
    appended = f"{current_text}\n\n## Update\n{additional_text.strip()}\n"

    new_version = await tool_context.save_artifact(
        filename=normalized,
        artifact=_text_part(appended, mime_type="text/markdown"),
    )

    return {
        "status": "success",
        "filename": normalized,
        "version": new_version,
        "report": f"Appended content and saved {normalized} as version {new_version}.",
    }


async def read_note_artifact(filename: str, tool_context: ToolContext, version: int | None = None) -> dict:
    """Read a note artifact by filename and optional version.

    Args:
        filename: Artifact filename to load.
        tool_context: ADK tool context for artifact operations.
        version: Specific version to fetch; latest when omitted.

    Returns:
        Dict containing the loaded content or not-found details.
    """
    normalized = _normalize_filename(filename)
    artifact = await tool_context.load_artifact(filename=normalized, version=version)

    if artifact is None:
        available = await tool_context.list_artifacts()
        return {
            "status": "error",
            "error": "artifact_not_found",
            "filename": normalized,
            "available_files": sorted(available),
            "report": f"Artifact '{normalized}' not found.",
        }

    return {
        "status": "success",
        "filename": normalized,
        "requested_version": version,
        "content": _part_to_text(artifact),
        "report": f"Loaded {normalized}" + (f" version {version}." if version is not None else " (latest version)."),
    }


async def list_note_artifacts(tool_context: ToolContext) -> dict:
    """List artifact keys available in the current artifact context.

    Args:
        tool_context: ADK tool context for artifact operations.

    Returns:
        Dict containing artifact filenames and total count.
    """
    filenames = sorted(await tool_context.list_artifacts())
    return {
        "status": "success",
        "count": len(filenames),
        "filenames": filenames,
        "report": f"Found {len(filenames)} artifact file(s).",
    }


async def save_user_profile_artifact(profile_text: str, tool_context: ToolContext) -> dict:
    """Save viewer/profile preferences as a text artifact.

    Args:
        profile_text: Preference text to persist.
        tool_context: ADK tool context for artifact operations.

    Returns:
        Dict with save status, target filename, and version.
    """
    user_id = tool_context.user_id or "default_user"
    filename = "user:viewer_profile.md"

    version = await tool_context.save_artifact(
        filename=filename,
        artifact=_text_part(profile_text.strip(), mime_type="text/plain"),
    )

    return {
        "status": "success",
        "filename": filename,
        "user_id": user_id,
        "version": version,
        "report": f"Saved user profile for '{user_id}' as {filename} (version {version}).",
    }


async def read_user_profile_artifact(tool_context: ToolContext) -> dict:
    """Load the saved viewer profile artifact.

    Args:
        tool_context: ADK tool context for artifact operations.

    Returns:
        Dict containing profile content or a not-found error payload.
    """
    user_id = tool_context.user_id or "default_user"
    filename = "user:viewer_profile.md"

    artifact = await tool_context.load_artifact(filename=filename)
    if artifact is None:
        return {
            "status": "error",
            "error": "profile_not_found",
            "user_id": user_id,
            "report": "No saved user profile artifact found yet.",
        }

    return {
        "status": "success",
        "filename": filename,
        "user_id": user_id,
        "content": _part_to_text(artifact),
        "report": f"Loaded user profile artifact for '{user_id}'.",
    }


root_agent = Agent(
    name="artifact_notebook_agent",
    model="gemini-2.5-flash",
    description="Demonstrates ADK artifact save/load/list/version workflows.",
    instruction=ROOT_PROMPT,
    tools=[
        save_note_artifact,
        append_to_note_artifact,
        read_note_artifact,
        list_note_artifacts,
        save_user_profile_artifact,
        read_user_profile_artifact,
    ],
)

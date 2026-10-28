# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Netresearch DTT GmbH
"""Hermes Agent adapter for the portable file-search skill."""

from __future__ import annotations

from pathlib import Path
from typing import Any


_SEEN: set[tuple[str, str]] = set()


def _command(tool_name: str | None, args: Any) -> str:
    if tool_name not in {"terminal", "shell", "Bash"} or not isinstance(args, dict):
        return ""
    command = args.get("command")
    return command if isinstance(command, str) else ""


def _nudge(tool_name: str | None, args: Any, session_id: str | None = None, **_: Any) -> None:
    """Print a fail-open, once-per-rule reminder for Hermes terminal calls."""
    command = _command(tool_name, args)
    if not command:
        return

    import importlib.util

    path = Path(__file__).parent / "scripts" / "pre_bash_search_nudge.py"
    spec = importlib.util.spec_from_file_location("file_search_nudge", path)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for message in module.detect(command):
        key = (str(session_id or ""), message)
        if key in _SEEN:
            continue
        _SEEN.add(key)
        # Observer hooks must not alter or block the tool call.
        print(f"file-search: {message} (warned once per rule per session)")


def _search_policy(**_: Any) -> dict[str, str]:
    """Keep the skill's core rule visible when Hermes has not loaded the skill."""
    return {
        "context": (
            "File-search guidance: use rg instead of grep, fd instead of find, "
            "and ast-grep (sg) for structural code patterns."
        )
    }


def register(ctx: Any) -> None:
    """Register the bundled skill and Hermes-native compatibility hooks."""
    skill = Path(__file__).parent / "skills" / "file-search" / "SKILL.md"
    if skill.is_file():
        ctx.register_skill("file-search", skill)
    ctx.register_hook("pre_tool_call", _nudge)
    ctx.register_hook("pre_llm_call", _search_policy)

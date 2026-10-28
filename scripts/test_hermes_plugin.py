#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Smoke tests for the dependency-free Hermes native adapter."""

from pathlib import Path
import importlib.util

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("file_search_hermes", ROOT / "__init__.py")
assert SPEC and SPEC.loader
plugin = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plugin)


class Context:
    def __init__(self):
        self.skills = []
        self.hooks = []

    def register_skill(self, name, path):
        self.skills.append((name, Path(path)))

    def register_hook(self, name, callback):
        self.hooks.append((name, callback))


ctx = Context()
plugin.register(ctx)
assert ctx.skills == [("file-search", ROOT / "skills" / "file-search" / "SKILL.md")]
assert {name for name, _ in ctx.hooks} == {"pre_tool_call", "pre_llm_call"}

plugin._SEEN.clear()
callback = dict(ctx.hooks)["pre_tool_call"]
callback(tool_name="terminal", args={"command": "find . -name '*.py'"}, session_id="test")
callback(tool_name="terminal", args={"command": "find . -name '*.py'"}, session_id="test")
assert len(plugin._SEEN) == 1
assert plugin._search_policy()["context"].startswith("File-search guidance:")
print("Hermes adapter smoke tests passed")

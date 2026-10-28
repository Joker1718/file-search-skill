# Hermes Agent compatibility

This repository supports Hermes through both relevant plugin surfaces:

- The existing root `plugin.json` and `skills/file-search/SKILL.md` are a
  portable Agent Plugins v1 package. Hermes loads the skill as
  `file-search:file-search`.
- `plugin.yaml` and `__init__.py` provide the native Hermes adapter. The
  adapter registers the bundled skill, a fail-open `pre_tool_call` reminder
  for `terminal`/`shell`, and a small `pre_llm_call` context reminder.

Install the checkout as a native plugin by placing the repository directory at
`~/.hermes/plugins/file-search`, then enable and validate it:

```text
hermes plugins enable file-search
hermes plugins doctor ~/.hermes/plugins/file-search --ci
```

The native hook only prints a reminder and never blocks or rewrites a command.
The existing Claude Code `hooks/hooks.json` remains unchanged. The shared
`scripts/pre_bash_search_nudge.py` also accepts Hermes shell-hook payloads
(`tool_name: terminal` and `tool_input.command`) for users who prefer a
subprocess hook configured in Hermes' `config.yaml`.

Hermes does not execute Claude Code's `hooks/hooks.json`; configure that
integration in Hermes' own hook configuration when subprocess isolation is
preferred.

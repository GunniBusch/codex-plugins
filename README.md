# Codex Plugins

This repository contains a Codex plugin marketplace. It currently includes:

- `apple-mail`: compose visible drafts or send messages through the local macOS Apple Mail app.
- `llm-code-auditor`: model and improve AI-shaped code quality with code remodel markup, a quality lens, concrete scanner leads, benchmarks, and cleanup skills.

## Structure

```text
.agents/plugins/marketplace.json
plugins/apple-mail/
  .codex-plugin/plugin.json
  .mcp.json
  assets/
  scripts/
  skills/
```

Codex discovers the repo-local marketplace at `.agents/plugins/marketplace.json`. The Apple Mail plugin is stored in this repository as a local source. The LLM Code Auditor plugin is installed from its dedicated Git repository with a `source=url` entry and is marked `INSTALLED_BY_DEFAULT` so it is added to Codex when this marketplace is refreshed.

```text
https://github.com/GunniBusch/llm-code-auditor.git
```

## Apple Mail Plugin

The plugin exposes a local MCP server with two tools:

- `apple_mail_compose`: creates a visible draft in Apple Mail.
- `apple_mail_send`: sends through Apple Mail when `confirm_send: true` is provided.

macOS may ask for Automation permission the first time the MCP server controls Mail. Allow Codex or the terminal process to control Mail when prompted.

## LLM Code Auditor Plugin

The plugin bundles an umbrella skill, targeted cleanup skills, shared references, a code-remodel tool, a quality-lens tool, a scanner, and benchmark fixtures for reviewing generated or agent-written code. It focuses on higher-level code quality pressure first, then uses concrete leads as evidence for context-sensitive simplification, readable domain code, useful tests, and behavior-preserving cleanup.

## Development

Validate the plugin metadata and server syntax:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/apple-mail/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/apple-mail/.mcp.json >/dev/null
node --check plugins/apple-mail/scripts/apple-mail-mcp.mjs

# Validate the auditor plugin in its dedicated repository:
# UV_CACHE_DIR=/private/tmp/uv-cache uv run python scripts/validate.py
```

The repository URL used by plugin manifests is:

```text
https://github.com/GunniBusch/codex-plugins
```

## License

BSD 3-Clause. See `LICENSE`.

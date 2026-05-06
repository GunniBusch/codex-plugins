# Codex Plugins

This repository contains a Codex plugin marketplace. It currently includes:

- `apple-mail`: compose visible drafts or send messages through the local macOS Apple Mail app.
- `llm-code-auditor`: detect and fix likely LLM-generated code smells and over-engineered agent code.

## Structure

```text
.agents/plugins/marketplace.json
plugins/apple-mail/
  .codex-plugin/plugin.json
  .mcp.json
  assets/
  scripts/
  skills/
plugins/llm-code-auditor/
  .codex-plugin/plugin.json
  assets/
  skills/
```

Codex discovers the repo-local marketplace at `.agents/plugins/marketplace.json`. Plugin source paths point to `./plugins/<plugin-name>`, relative to the repository root.

## Apple Mail Plugin

The plugin exposes a local MCP server with two tools:

- `apple_mail_compose`: creates a visible draft in Apple Mail.
- `apple_mail_send`: sends through Apple Mail when `confirm_send: true` is provided.

macOS may ask for Automation permission the first time the MCP server controls Mail. Allow Codex or the terminal process to control Mail when prompted.

## LLM Code Auditor Plugin

The plugin bundles a skill and a small scanner for reviewing generated or agent-written code. It focuses on high-confidence generated-code patterns, context-sensitive simplification, and behavior-preserving cleanup.

## Development

Validate the plugin metadata and server syntax:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/apple-mail/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/apple-mail/.mcp.json >/dev/null
python3 -m json.tool plugins/llm-code-auditor/.codex-plugin/plugin.json >/dev/null
node --check plugins/apple-mail/scripts/apple-mail-mcp.mjs
python3 -m py_compile plugins/llm-code-auditor/skills/llm-code-auditor/scripts/llm_code_smell_scan.py
```

The repository URL used by plugin manifests is:

```text
https://github.com/GunniBusch/codex-plugins
```

## License

BSD 3-Clause. See `LICENSE`.

# Apple Mail Codex Plugin

This repository contains a Codex plugin marketplace with one plugin:

- `apple-mail`: compose visible drafts or send messages through the local macOS Apple Mail app.

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

Codex discovers the repo-local marketplace at `.agents/plugins/marketplace.json`. The plugin source path points to `./plugins/apple-mail`, relative to the repository root.

## Apple Mail Plugin

The plugin exposes a local MCP server with two tools:

- `apple_mail_compose`: creates a visible draft in Apple Mail.
- `apple_mail_send`: sends through Apple Mail when `confirm_send: true` is provided.

macOS may ask for Automation permission the first time the MCP server controls Mail. Allow Codex or the terminal process to control Mail when prompted.

## Development

Validate the plugin metadata and server syntax:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/apple-mail/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/apple-mail/.mcp.json >/dev/null
node --check plugins/apple-mail/scripts/apple-mail-mcp.mjs
```

After publishing this repository to GitHub, update `plugins/apple-mail/.codex-plugin/plugin.json` if the final repository URL differs from:

```text
https://github.com/GunniBusch/apple-mail-codex-plugin
```

## License

BSD 3-Clause. See `LICENSE`.

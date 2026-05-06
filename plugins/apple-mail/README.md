# Apple Mail

Codex plugin for composing and sending email through the local macOS Apple Mail app.

## Components

- `.codex-plugin/plugin.json`: plugin manifest and install-surface metadata.
- `.mcp.json`: bundled MCP server configuration.
- `scripts/apple-mail-mcp.mjs`: stdio MCP server that calls `/usr/bin/osascript`.
- `skills/apple-mail/SKILL.md`: usage guidance for drafting and sending safely.
- `assets/`: plugin icon assets.

## Tools

- `apple_mail_compose`
  - Required: `to`, `subject`, `body`
  - Optional: `cc`, `bcc`, `sender`
  - Opens a visible Apple Mail draft.

- `apple_mail_send`
  - Required: `to`, `subject`, `body`, `confirm_send`
  - Optional: `cc`, `bcc`, `sender`
  - Sends immediately only when `confirm_send` is `true`.

## Notes

The server uses AppleScript through `osascript`, so it only works on macOS with Apple Mail installed and configured. The first run may require granting Automation permissions.

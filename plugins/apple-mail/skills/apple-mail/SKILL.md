---
name: apple-mail
description: Send or draft email through Apple Mail on macOS. Use when the user asks to compose, draft, or send email via Apple Mail.
---

# Apple Mail

Use this skill when the user wants Codex to compose, draft, or send email through the local macOS Apple Mail app.

## Workflow

1. Prefer `apple_mail_compose` when the user has not explicitly asked to send immediately. It creates a visible Apple Mail draft for review.
2. Use `apple_mail_send` only when the user explicitly asks to send the message and the tool call includes `confirm_send: true`.
3. Before direct sending, make sure the recipient list, subject, and body are known. Ask for missing required fields.
4. If macOS asks for Automation permission, the user must allow Codex or Terminal to control Mail.

## Tools

- `apple_mail_compose`: creates a visible draft in Apple Mail.
- `apple_mail_send`: sends through Apple Mail after explicit confirmation.

Required fields for both tools are `to`, `subject`, and `body`. Optional fields are `cc`, `bcc`, and `sender`.

#!/usr/bin/env node
import { execFile } from "node:child_process";
import { stdin, stdout } from "node:process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const serverInfo = { name: "apple-mail", version: "0.1.0" };

const tools = [
  {
    name: "apple_mail_compose",
    description: "Create a visible draft message in macOS Apple Mail.",
    inputSchema: {
      type: "object",
      additionalProperties: false,
      properties: {
        to: {
          type: "array",
          items: { type: "string" },
          minItems: 1,
          description: "Recipient email addresses."
        },
        subject: { type: "string" },
        body: { type: "string" },
        cc: {
          type: "array",
          items: { type: "string" },
          default: []
        },
        bcc: {
          type: "array",
          items: { type: "string" },
          default: []
        },
        sender: {
          type: "string",
          description: "Optional Mail sender account/address."
        }
      },
      required: ["to", "subject", "body"]
    }
  },
  {
    name: "apple_mail_send",
    description: "Send a message through macOS Apple Mail. Requires confirm_send: true.",
    inputSchema: {
      type: "object",
      additionalProperties: false,
      properties: {
        to: {
          type: "array",
          items: { type: "string" },
          minItems: 1,
          description: "Recipient email addresses."
        },
        subject: { type: "string" },
        body: { type: "string" },
        cc: {
          type: "array",
          items: { type: "string" },
          default: []
        },
        bcc: {
          type: "array",
          items: { type: "string" },
          default: []
        },
        sender: {
          type: "string",
          description: "Optional Mail sender account/address."
        },
        confirm_send: {
          type: "boolean",
          description: "Must be true to send immediately."
        }
      },
      required: ["to", "subject", "body", "confirm_send"]
    }
  }
];

let inputBuffer = Buffer.alloc(0);

stdin.on("data", (chunk) => {
  inputBuffer = Buffer.concat([inputBuffer, chunk]);
  drainMessages().catch((error) => {
    writeLog(`Fatal MCP parsing error: ${error.stack || error.message}`);
  });
});

function drainMessages() {
  while (true) {
    const headerEnd = inputBuffer.indexOf("\r\n\r\n");
    if (headerEnd === -1) {
      return Promise.resolve();
    }

    const header = inputBuffer.subarray(0, headerEnd).toString("utf8");
    const match = /^Content-Length:\s*(\d+)/im.exec(header);
    if (!match) {
      inputBuffer = Buffer.alloc(0);
      throw new Error("Missing Content-Length header");
    }

    const contentLength = Number(match[1]);
    const messageStart = headerEnd + 4;
    const messageEnd = messageStart + contentLength;
    if (inputBuffer.length < messageEnd) {
      return Promise.resolve();
    }

    const payload = inputBuffer.subarray(messageStart, messageEnd).toString("utf8");
    inputBuffer = inputBuffer.subarray(messageEnd);
    void handleMessage(JSON.parse(payload));
  }
}

async function handleMessage(message) {
  if (!Object.prototype.hasOwnProperty.call(message, "id")) {
    return;
  }

  try {
    const result = await routeRequest(message.method, message.params || {});
    writeMessage({ jsonrpc: "2.0", id: message.id, result });
  } catch (error) {
    writeMessage({
      jsonrpc: "2.0",
      id: message.id,
      error: {
        code: error.code || -32603,
        message: error.message || "Internal error"
      }
    });
  }
}

async function routeRequest(method, params) {
  if (method === "initialize") {
    return {
      protocolVersion: "2024-11-05",
      capabilities: { tools: {} },
      serverInfo
    };
  }

  if (method === "ping") {
    return {};
  }

  if (method === "tools/list") {
    return { tools };
  }

  if (method === "tools/call") {
    return callTool(params);
  }

  const error = new Error(`Unsupported method: ${method}`);
  error.code = -32601;
  throw error;
}

async function callTool(params) {
  const name = params.name;
  const args = params.arguments || {};

  if (name === "apple_mail_compose") {
    const normalized = normalizeMessageArgs(args);
    await runMailScript({ ...normalized, action: "draft" });
    return textResult(`Created Apple Mail draft to ${normalized.to.join(", ")}.`);
  }

  if (name === "apple_mail_send") {
    if (args.confirm_send !== true) {
      throw new Error("Refusing to send because confirm_send is not true.");
    }
    const normalized = normalizeMessageArgs(args);
    await runMailScript({ ...normalized, action: "send" });
    return textResult(`Sent Apple Mail message to ${normalized.to.join(", ")}.`);
  }

  const error = new Error(`Unknown tool: ${name}`);
  error.code = -32602;
  throw error;
}

function normalizeMessageArgs(args) {
  const to = normalizeAddressList(args.to, "to");
  const cc = normalizeAddressList(args.cc || [], "cc");
  const bcc = normalizeAddressList(args.bcc || [], "bcc");
  const subject = requiredString(args.subject, "subject");
  const body = requiredString(args.body, "body");
  const sender = args.sender == null ? "" : String(args.sender).trim();

  return { to, cc, bcc, subject, body, sender };
}

function normalizeAddressList(value, fieldName) {
  if (!Array.isArray(value)) {
    throw new Error(`${fieldName} must be an array of email addresses.`);
  }

  const addresses = value.map((item) => String(item).trim()).filter(Boolean);
  if (fieldName === "to" && addresses.length === 0) {
    throw new Error("to must include at least one recipient.");
  }
  return addresses;
}

function requiredString(value, fieldName) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${fieldName} must be a non-empty string.`);
  }
  return value;
}

async function runMailScript({ to, cc, bcc, subject, body, sender, action }) {
  const script = `
on run argv
  set subjectText to item 1 of argv
  set bodyText to item 2 of argv
  set toText to item 3 of argv
  set ccText to item 4 of argv
  set bccText to item 5 of argv
  set senderText to item 6 of argv
  set actionText to item 7 of argv

  tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:subjectText, content:bodyText, visible:true}
    repeat with addressValue in paragraphs of toText
      set cleanAddress to addressValue as text
      if cleanAddress is not "" then
        tell newMessage to make new to recipient at end of to recipients with properties {address:cleanAddress}
      end if
    end repeat
    repeat with addressValue in paragraphs of ccText
      set cleanAddress to addressValue as text
      if cleanAddress is not "" then
        tell newMessage to make new cc recipient at end of cc recipients with properties {address:cleanAddress}
      end if
    end repeat
    repeat with addressValue in paragraphs of bccText
      set cleanAddress to addressValue as text
      if cleanAddress is not "" then
        tell newMessage to make new bcc recipient at end of bcc recipients with properties {address:cleanAddress}
      end if
    end repeat
    if senderText is not "" then set sender of newMessage to senderText
    if actionText is "send" then
      send newMessage
    else
      activate
    end if
  end tell
end run
`;

  const args = [
    "-e",
    script,
    subject,
    body,
    to.join("\n"),
    cc.join("\n"),
    bcc.join("\n"),
    sender,
    action
  ];

  try {
    await execFileAsync("/usr/bin/osascript", args, {
      timeout: 30000,
      maxBuffer: 1024 * 1024
    });
  } catch (error) {
    const stderr = error.stderr ? String(error.stderr).trim() : "";
    const reason = stderr || error.message;
    throw new Error(`Apple Mail automation failed: ${reason}`);
  }
}

function textResult(text) {
  return {
    content: [{ type: "text", text }]
  };
}

function writeMessage(message) {
  const payload = JSON.stringify(message);
  stdout.write(`Content-Length: ${Buffer.byteLength(payload, "utf8")}\r\n\r\n${payload}`);
}

function writeLog(message) {
  process.stderr.write(`${message}\n`);
}

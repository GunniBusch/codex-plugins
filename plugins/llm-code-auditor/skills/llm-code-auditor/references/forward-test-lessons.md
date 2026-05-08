# Forward-Test Lessons

Use this when real agents produce false positives or awkward behavior while using the LLM Code Auditor plugin.

## LSP Capability Names

Observed transcript:

- Scanner flagged `codeActionProvider` as `naming-inflation`.
- In an LSP server, `codeActionProvider` is a protocol capability name.

Rule:

- Keep external vocabulary when it is part of a protocol, framework, schema, generated client, or serialized API. This includes nested option fields such as LSP `resolveProvider`.
- Improve local wrapper names, comments, or structure around the contract instead of renaming the contract field.
- Add scanner exceptions only when the name is known contractual and common enough to recur.

## Ignored Build Output

Observed transcript:

- Tests depended on `server/out/server.cjs`.
- `server/out` was ignored.
- The correct fix was to make `npm test` build first, not to commit generated files.

Rule:

- If clean checkout behavior depends on ignored/generated output, fix scripts or test setup.
- Do not make source control carry stale generated artifacts unless the project intentionally versions them.

## Protocol Smoke Tests

Observed transcript:

- `node server/out/server.cjs --stdio < /dev/null` exited nonzero.
- That can be expected for an interactive protocol server with no session.
- The useful signal was absence of the original dynamic-require crash.

Rule:

- Define the exact smoke-test signal before interpreting exit code.
- For protocol servers, use a real minimal protocol handshake when possible.
- If using closed stdin, report it as "startup crash probe", not "server works."

## Missing Protocol Transport Arguments

Observed transcript:

- Zed launched `server.cjs`.
- The server threw: `Connection input stream is not set. Use arguments ... '--node-ipc', '--stdio' or '--socket={number}'`.
- This means the executable started, but the launcher did not provide the transport expected by the protocol runtime.

Rule:

- Check the wrapper/package command before changing the protocol server.
- Add or test the required transport, for example stdio, IPC, socket, port, URL, or explicit streams.
- Keep a regression test near the wrapper, because source tests can pass while launcher args are wrong.

## Scanner Improvement Policy

- Do not suppress a class of findings because one example is false positive.
- Add evidence, severity, or a precise exception.
- Prefer scanner output that teaches the next agent why a finding is weak.

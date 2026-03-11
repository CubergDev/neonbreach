# AGENT OPERATING INSTRUCTIONS

## PowerShell 7 Profile Policy (Mandatory)

Do not load PowerShell profiles under any circumstances.

- Always run PowerShell commands with non-login semantics.
- When using shell tooling that supports it, set `login: false`.
- When invoking `pwsh` directly, always include `-NoProfile`.
- Prefer this form for direct invocation:
    - `pwsh -NoLogo -NoProfile -Command "<command>"`
- Do not use command forms that trigger profile loading.

## Rationale

This repository environment has profile scripts that can add noise/errors and slow execution. All automation should run
in a clean shell context.

---
name: himalaya
description: "CLI to manage emails via IMAP/SMTP. Use `himalaya` to list, read, write, reply, forward, search, and organize emails from the terminal. Supports multiple accounts and message composition with MML (MIME Meta Language)."
homepage: https://github.com/pimalaya/himalaya
metadata:
  {
    "openclaw":
      {
        "emoji": "📧",
        "requires": { "bins": ["himalaya"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "himalaya",
              "bins": ["himalaya"],
              "label": "Install Himalaya (brew)",
            },
          ],
      },
  }
---

# Himalaya Email CLI

CLI email client for managing emails from the terminal using IMAP, SMTP, Notmuch, or Sendmail backends.

## References

- `references/configuration.md` — config file setup + IMAP/SMTP authentication
- `references/message-composition.md` — MML syntax for composing emails

## Prerequisites

1. Himalaya CLI installed (`himalaya --version`)
2. Config file at `~/.config/himalaya/config.toml`
3. IMAP/SMTP credentials configured

## Configuration

Run the interactive wizard:

```bash
himalaya account configure
```

Or create `~/.config/himalaya/config.toml` manually:

```toml
[accounts.personal]
email = "you@example.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"
```

## Common Operations

```bash
# Folders
himalaya folder list

# List emails (default: INBOX)
himalaya envelope list
himalaya envelope list --folder "Sent"
himalaya envelope list --page 1 --page-size 20

# Search
himalaya envelope list from john@example.com subject meeting

# Read
himalaya message read 42
himalaya message export 42 --full          # raw MIME

# Reply / Forward
himalaya message reply 42
himalaya message reply 42 --all
himalaya message forward 42

# Compose
himalaya message write                     # opens $EDITOR

# Send directly via template
cat << 'EOF' | himalaya template send
From: you@example.com
To: recipient@example.com
Subject: Test Message

Hello from Himalaya!
EOF

# Move / Copy / Delete
himalaya message move 42 "Archive"
himalaya message copy 42 "Important"
himalaya message delete 42

# Flags
himalaya flag add 42 --flag seen
himalaya flag remove 42 --flag seen

# Attachments
himalaya attachment download 42
himalaya attachment download 42 --dir ~/Downloads
```

## Multiple Accounts

```bash
himalaya account list
himalaya --account work envelope list
```

## Output Formats

```bash
himalaya envelope list --output json
himalaya envelope list --output plain
```

## Debugging

```bash
RUST_LOG=debug himalaya envelope list
RUST_LOG=trace RUST_BACKTRACE=1 himalaya envelope list
```

## Tips

- Message IDs are relative to the current folder; re-list after folder changes.
- For rich emails with attachments, use MML syntax (see `references/message-composition.md`).
- Store passwords securely using `pass`, system keyring, or a command that outputs the password.

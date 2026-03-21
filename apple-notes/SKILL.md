---
name: apple-notes
description: Manage Apple Notes via the `memo` CLI on macOS (create, view, edit, delete, search, move, and export notes). Use when a user asks OpenClaw to add a note, list notes, search notes, or manage note folders.
homepage: https://github.com/antoniorodr/memo
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "os": ["darwin"],
        "requires": { "bins": ["memo"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "antoniorodr/memo/memo",
              "bins": ["memo"],
              "label": "Install memo via Homebrew",
            },
          ],
      },
  }
---

# Apple Notes CLI

Use `memo notes` to manage Apple Notes directly from the terminal. Create, view, edit, delete, search, move notes between folders, and export to HTML/Markdown.

Setup

- Install (Homebrew): `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Manual (pip): `pip install .` (after cloning the repo)
- macOS-only; if prompted, grant Automation access to Notes.app.

View Notes

- List all notes: `memo notes`
- Filter by folder: `memo notes -f "Folder Name"`
- Search notes (fuzzy): `memo notes -s "query"`

Create Notes

- Add a new note: `memo notes -a` (opens interactive editor)
- Quick add with title: `memo notes -a "Note Title"`

Edit Notes

- Edit existing note: `memo notes -e` (interactive selection)

Delete Notes

- Delete a note: `memo notes -d` (interactive selection)

Move Notes

- Move note to folder: `memo notes -m` (interactive selection)

Export Notes

- Export to HTML/Markdown: `memo notes -ex`

Limitations

- macOS-only; requires Apple Notes.app to be accessible.
- Cannot edit notes containing images or attachments.
- Interactive prompts require terminal access.
- For automation, grant permissions in System Settings > Privacy & Security > Automation.

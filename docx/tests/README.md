# DOCX Regression Tests

## Structure

```
tests/
├── fixtures/     ← Test input files (.docx)
│   ├── tracked_changes.docx   ← DOCX with insertions/deletions
│   ├── comments.docx          ← DOCX with comment markers
│   └── broken_rels.docx       ← DOCX with orphan relationships
├── expected/     ← Expected outputs (JSON/TXT)
│   ├── validate_tracked_changes.json
│   ├── validate_broken_rels.json
│   ├── repair_broken_rels.json
│   └── text_comments.txt
└── README.md
```

## Running

```bash
# Validate a fixture
python docx_cli.py validate tests/fixtures/broken_rels.docx --json | diff - tests/expected/validate_broken_rels.json

# Repair dry-run
python docx_cli.py repair tests/fixtures/broken_rels.docx --json | diff - tests/expected/repair_broken_rels.json

# Text extraction
python docx_cli.py text tests/fixtures/comments.docx | diff - tests/expected/text_comments.txt
```

## Adding Tests

1. Place fixture file in `fixtures/`
2. Run the CLI command and verify output manually
3. Save verified output to `expected/`
4. Add a comment in this README describing the test case

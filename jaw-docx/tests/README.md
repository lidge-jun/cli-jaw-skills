# DOCX Regression Tests

## Structure

```
tests/
├── fixtures/     ← Test input files (.docx)
│   ├── tracked_changes.docx   ← DOCX with insertions/deletions
│   ├── tracked_changes_header_footer.docx ← Revisions in header/footer parts
│   ├── comments.docx          ← DOCX with comment markers
│   ├── comment_mid_run_exact.docx ← Anchor starts/ends mid-run
│   ├── comment_multi_t_single_run.docx ← One run with multiple `w:t` nodes
│   ├── comment_hyperlink_boundary.docx ← Anchor matches hyperlink container text
│   ├── comment_field_code_boundary.docx ← Anchor matches field result text
│   └── broken_rels.docx       ← DOCX with orphan relationships
├── expected/     ← Expected outputs (JSON/TXT)
│   ├── validate_tracked_changes.json
│   ├── validate_tracked_changes_header_footer.json
│   ├── accept_changes_header_footer_zero.txt
│   ├── comment_mid_run_exact.json
│   ├── comment_multi_t_single_run.json
│   ├── comment_hyperlink_boundary.json
│   ├── comment_field_code_boundary.json
│   ├── validate_broken_rels.json
│   ├── repair_broken_rels.json
│   └── text_comments.txt
└── README.md
```

## Running

```bash
# Full regression suite (includes accept_changes + exact anchor boundary checks)
python ../scripts/run_tests.py

# Rebuild fixtures and expected outputs
python generate_fixtures.py build --force

# Verify fixture integrity
python generate_fixtures.py verify

# Validate a fixture
python docx_cli.py validate tests/fixtures/broken_rels.docx --json | diff - tests/expected/validate_broken_rels.json

# Repair dry-run
python docx_cli.py repair tests/fixtures/broken_rels.docx --json | diff - tests/expected/repair_broken_rels.json

# Text extraction
python docx_cli.py text tests/fixtures/comments.docx | diff - tests/expected/text_comments.txt
```

## Adding Tests

1. Add or update the generator helper first
2. Run `python generate_fixtures.py build --only <slug>`
3. Run `python generate_fixtures.py verify --only <slug>`
4. Run `python ../scripts/run_tests.py -v`

## Covered P0 Regressions

- `accept_changes.py` removes tracked-change markup from the shipped tracked-changes fixture
- `accept_changes.py` removes revision markup from body, header, and footer parts
- `comment.py` isolates exact anchor boundaries even when the anchor starts/ends mid-run
- `comment.py` keeps exact ranges for multi-`w:t`, hyperlink, and field-adjacent anchors

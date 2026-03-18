# PPTX Regression Tests

## Structure

```
tests/
├── fixtures/     ← Test input files (.pptx)
│   ├── basic_slides.pptx      ← Simple 3-slide deck for text/thumbnail
│   ├── orphan_media.pptx      ← PPTX with unreferenced media files
│   └── broken_layout.pptx     ← PPTX with missing layout references
├── expected/     ← Expected outputs (JSON/TXT)
│   ├── validate_broken_layout.json
│   ├── repair_broken_layout.json
│   ├── text_basic_slides.txt
│   └── clean_orphan_media.txt
└── README.md
```

## Running

```bash
# Validate a fixture
python pptx_cli.py validate tests/fixtures/broken_layout.pptx --json | diff - tests/expected/validate_broken_layout.json

# Text extraction
python pptx_cli.py text tests/fixtures/basic_slides.pptx | diff - tests/expected/text_basic_slides.txt

# Clean dry-run
python pptx_cli.py clean tests/fixtures/orphan_media_unpacked/ | diff - tests/expected/clean_orphan_media.txt
```

## Adding Tests

1. Place fixture file in `fixtures/`
2. Run the CLI command and verify output manually
3. Save verified output to `expected/`
4. Add a comment in this README describing the test case

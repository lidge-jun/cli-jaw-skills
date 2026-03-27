# PPTX Regression Tests

## Structure

```
tests/
├── fixtures/     ← Test input files (.pptx)
│   ├── basic_slides.pptx      ← Simple 3-slide deck for text/thumbnail
│   ├── blankless_minimal_deck.pptx ← No slideLayouts/ directory
│   ├── blank_layout_named_nonstandard.pptx ← Layout exists but name is non-standard
│   ├── duplicate_media_chart_deck.pptx ← Slide rels include image + chart targets
│   ├── notes_reuse_conflict.pptx ← Two slides reference the same notes slide
│   ├── orphan_media.pptx      ← PPTX with unreferenced media files
│   └── broken_layout.pptx     ← PPTX with missing layout references
├── metadata/     ← Manual-fixture verification metadata
│   ├── duplicate_media_chart_deck.meta.json
│   └── notes_reuse_conflict.meta.json
├── expected/     ← Expected outputs (JSON/TXT)
│   ├── validate_broken_layout.json
│   ├── validate_blankless_minimal_deck.json
│   ├── validate_blank_layout_named_nonstandard.json
│   ├── duplicate_media_chart_summary.json
│   └── notes_reuse_conflict.json
│   ├── repair_broken_layout.json
│   ├── text_basic_slides.txt
│   └── validate_basic_slides.json
└── README.md
```

## Running

```bash
# Full regression suite (includes add_slide.py --blank on the shipped basic fixture)
python ../scripts/run_tests.py

# Rebuild fixtures and metadata
python generate_fixtures.py build --force

# Verify fixture integrity
python generate_fixtures.py verify

# Validate a fixture
python pptx_cli.py validate tests/fixtures/broken_layout.pptx --json | diff - tests/expected/validate_broken_layout.json

# Text extraction
python pptx_cli.py text tests/fixtures/basic_slides.pptx | diff - tests/expected/text_basic_slides.txt

# Clean dry-run
python pptx_cli.py open tests/fixtures/orphan_media.pptx /tmp/orphan_media_unpacked
python pptx_cli.py clean /tmp/orphan_media_unpacked
```

## Adding Tests

1. Prefer generator changes over manual zip editing
2. If a fixture must stay manual, add/update its `.meta.json`
3. Run `python generate_fixtures.py verify`
4. Run `python ../scripts/run_tests.py -v`

## Covered P0 Regressions

- `add_slide.py --blank` must pack and validate successfully on `basic_slides.pptx`
- `add_slide.py --blank` must also validate on `blankless_minimal_deck.pptx`
- `add_slide.py --blank` must choose a valid layout path on `blank_layout_named_nonstandard.pptx`
- `duplicate_slide()` must preserve image/chart rel targets on `duplicate_media_chart_deck.pptx`
- validator must surface duplicate notes-slide references on `notes_reuse_conflict.pptx`

## Fixture Differences

- `orphan_media.pptx`: media file exists but no slide references it.
- `duplicate_media_chart_deck.pptx`: slide relationships exist and must remain valid after duplication.

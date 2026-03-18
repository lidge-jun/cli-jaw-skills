# XLSX Regression Tests

## Structure

```
tests/
├── fixtures/     ← Test input files (.xlsx)
│   ├── formula_errors.xlsx    ← XLSX with #REF!, #DIV/0! errors
│   ├── multi_sheet.xlsx       ← XLSX with 3+ sheets for overview test
│   └── broken_refs.xlsx       ← XLSX with broken sharedString refs
├── expected/     ← Expected outputs (JSON/TXT)
│   ├── validate_broken_refs.json
│   ├── formula_audit_errors.json
│   ├── sheet_overview_multi.json
│   └── text_multi_sheet.txt
└── README.md
```

## Running

```bash
# Validate a fixture
python xlsx_cli.py validate tests/fixtures/broken_refs.xlsx --json | diff - tests/expected/validate_broken_refs.json

# Formula audit
python xlsx_cli.py formula-audit tests/fixtures/formula_errors.xlsx --json | diff - tests/expected/formula_audit_errors.json

# Sheet overview
python xlsx_cli.py sheet-overview tests/fixtures/multi_sheet.xlsx --json | diff - tests/expected/sheet_overview_multi.json
```

## Adding Tests

1. Place fixture file in `fixtures/`
2. Run the CLI command and verify output manually
3. Save verified output to `expected/`
4. Add a comment in this README describing the test case

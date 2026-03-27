# XLSX Regression Tests

## Structure

```
tests/
├── fixtures/     ← Test input files (.xlsx)
│   ├── formula_errors.xlsx    ← XLSX with #REF!, #DIV/0! errors
│   ├── formula_uncached.xlsx  ← XLSX with formulas but no cached values
│   ├── multi_sheet.xlsx       ← XLSX with 3+ sheets for overview test
│   ├── wide_columns_ad.xlsx   ← 30-column sheet to stress overview width handling
│   ├── korean_identifier_stress.xlsx ← Korean sheet/header/search stress fixture
│   └── broken_refs.xlsx       ← XLSX with broken sharedString refs
├── expected/     ← Expected outputs (JSON/TXT)
│   ├── validate_broken_refs.json
│   ├── formula_audit_errors.json
│   ├── formula_audit_uncached.json
│   ├── sheet_overview_multi.json
│   ├── sheet_overview_wide_columns_ad.json
│   ├── search_korean_identifier_stress.json
│   └── text_multi_sheet.txt
└── README.md
```

## Running

```bash
# Full regression suite
python ../scripts/run_tests.py

# Rebuild fixtures and expected outputs
python generate_fixtures.py build --force

# Verify fixture integrity
python generate_fixtures.py verify

# Validate a fixture
python xlsx_cli.py validate tests/fixtures/broken_refs.xlsx --json | diff - tests/expected/validate_broken_refs.json

# Formula audit
python xlsx_cli.py formula-audit tests/fixtures/formula_errors.xlsx --json | diff - tests/expected/formula_audit_errors.json

# Sheet overview
python xlsx_cli.py sheet-overview tests/fixtures/multi_sheet.xlsx --json | diff - tests/expected/sheet_overview_multi.json
```

## Adding Tests

1. Add or update the generator helper first
2. Run `python generate_fixtures.py build --only <slug>`
3. Run `python generate_fixtures.py verify --only <slug>`
4. Run `python ../scripts/run_tests.py -v`

## Fixture Differences

- `formula_errors.xlsx`: cached results are explicit Excel error values.
- `formula_uncached.xlsx`: formulas exist, but `data_only=True` reads no cached result values.

---
name: sarif-parsing
description: Parse, analyze, and process SARIF (Static Analysis Results Interchange Format) files. Use when reading security scan results, aggregating findings from multiple tools, deduplicating alerts, extracting specific vulnerabilities, or integrating SARIF data into CI/CD pipelines.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# SARIF Parsing

Parse, analyze, and process SARIF files from static analysis tools.
Out of scope: running scans (use CodeQL/Semgrep skills), writing rules, analyzing source code directly.

## SARIF Structure Overview

SARIF 2.1.0 is the current OASIS standard:

```
sarifLog
├── version: "2.1.0"
└── runs[]
    ├── tool
    │   ├── driver
    │   │   ├── name (required)
    │   │   ├── version
    │   │   └── rules[]
    │   └── extensions[]
    ├── results[]
    │   ├── ruleId
    │   ├── level (error/warning/note)
    │   ├── message.text
    │   ├── locations[]
    │   │   └── physicalLocation
    │   │       ├── artifactLocation.uri
    │   │       └── region (startLine, startColumn, etc.)
    │   ├── fingerprints{}
    │   └── partialFingerprints{}
    └── artifacts[]
```

### Why Fingerprinting Matters

Fingerprints hash content (code snippet, rule ID, relative location) to create stable identifiers regardless of environment. Without them, baseline comparison, regression detection, and suppression all fail — because tools report different paths across environments.

## Tool Selection

| Use Case | Tool | Install |
|----------|------|---------|
| Quick CLI queries | jq | `brew install jq` / `apt install jq` |
| Python (simple) | pysarif | `pip install pysarif` |
| Python (advanced) | sarif-tools | `pip install sarif-tools` |
| .NET | SARIF SDK | NuGet |
| JavaScript | sarif-js | npm |
| Go | garif | `go get github.com/chavacava/garif` |
| Validation | SARIF Validator | sarifweb.azurewebsites.net |

## Quick Analysis with jq

```bash
# Count total findings
jq '[.runs[].results[]] | length' results.sarif

# List all triggered rule IDs
jq '[.runs[].results[].ruleId] | unique' results.sarif

# Extract errors only
jq '.runs[].results[] | select(.level == "error")' results.sarif

# Findings with file locations
jq '.runs[].results[] | {
  rule: .ruleId,
  message: .message.text,
  file: .locations[0].physicalLocation.artifactLocation.uri,
  line: .locations[0].physicalLocation.region.startLine
}' results.sarif

# Count per rule at error level
jq '[.runs[].results[] | select(.level == "error")] | group_by(.ruleId) | map({rule: .[0].ruleId, count: length})' results.sarif

# Filter by specific file
jq --arg file "src/auth.py" '.runs[].results[] | select(.locations[].physicalLocation.artifactLocation.uri | contains($file))' results.sarif
```

## Python with pysarif

```python
from pysarif import load_from_file, save_to_file

sarif = load_from_file("results.sarif")
for run in sarif.runs:
    for result in run.results:
        print(f"  [{result.level}] {result.rule_id}: {result.message.text}")
        if result.locations:
            loc = result.locations[0].physical_location
            if loc and loc.artifact_location:
                print(f"    File: {loc.artifact_location.uri}:{loc.region.start_line if loc.region else '?'}")

save_to_file(sarif, "modified.sarif")
```

## Python with sarif-tools

```python
from sarif import loader

sarif_data = loader.load_sarif_file("results.sarif")
sarif_set = loader.load_sarif_files(["tool1.sarif", "tool2.sarif"])  # multi-file

report = sarif_data.get_report()
errors = report.get_issue_type_histogram_for_severity("error")
```

**sarif-tools CLI:**

```bash
sarif summary results.sarif
sarif ls --level error results.sarif
sarif diff baseline.sarif current.sarif     # find new/fixed issues
sarif csv results.sarif > results.csv
sarif html results.sarif > report.html
```

## Aggregating Multiple SARIF Files

```python
import json

def aggregate_sarif_files(sarif_paths: list[str]) -> dict:
    aggregated = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": []
    }
    for path in sarif_paths:
        with open(path) as f:
            aggregated["runs"].extend(json.load(f).get("runs", []))
    return aggregated

def deduplicate_results(sarif: dict) -> dict:
    """Remove duplicates based on fingerprints, falling back to rule+location key."""
    seen = set()
    for run in sarif["runs"]:
        unique = []
        for result in run.get("results", []):
            fp = None
            if result.get("partialFingerprints"):
                fp = tuple(sorted(result["partialFingerprints"].items()))
            elif result.get("fingerprints"):
                fp = tuple(sorted(result["fingerprints"].items()))
            else:
                loc = result.get("locations", [{}])[0]
                phys = loc.get("physicalLocation", {})
                fp = (result.get("ruleId"),
                      phys.get("artifactLocation", {}).get("uri"),
                      phys.get("region", {}).get("startLine"))
            if fp not in seen:
                seen.add(fp)
                unique.append(result)
        run["results"] = unique
    return sarif
```

## Common Pitfalls

### Path Normalization

Different tools report paths differently (absolute, relative, URI-encoded):

```python
from urllib.parse import unquote
from pathlib import Path

def normalize_path(uri: str, base_path: str = "") -> str:
    if uri.startswith("file://"):
        uri = uri[7:]
    uri = unquote(uri)
    if not Path(uri).is_absolute() and base_path:
        uri = str(Path(base_path) / uri)
    return str(Path(uri))
```

### Fingerprint Mismatch Across Runs

Fingerprints may differ when file paths, tool versions, or code formatting change between runs. Use a content-based fingerprint as fallback:

```python
import hashlib

def compute_stable_fingerprint(result: dict, file_content: str = None) -> str:
    components = [result.get("ruleId", ""), result.get("message", {}).get("text", "")[:100]]
    if file_content and result.get("locations"):
        region = result["locations"][0].get("physicalLocation", {}).get("region", {})
        if region.get("startLine"):
            lines = file_content.split("\n")
            idx = region["startLine"] - 1
            if 0 <= idx < len(lines):
                components.append(lines[idx].strip())
    return hashlib.sha256("".join(components).encode()).hexdigest()[:16]
```

### Missing or Incomplete Data

SARIF allows many optional fields. Use defensive access:

```python
def safe_get_location(result: dict) -> tuple[str, int]:
    try:
        loc = result.get("locations", [{}])[0]
        phys = loc.get("physicalLocation", {})
        return (phys.get("artifactLocation", {}).get("uri", "unknown"),
                phys.get("region", {}).get("startLine", 0))
    except (IndexError, KeyError, TypeError):
        return "unknown", 0
```

### Large File Performance

For 100MB+ SARIF files, stream instead of loading entirely:

```python
import ijson  # pip install ijson

def stream_results(sarif_path: str):
    with open(sarif_path, "rb") as f:
        for result in ijson.items(f, "runs.item.results.item"):
            yield result
```

### Schema Validation

Validate structure before processing:

```bash
# ajv-cli
ajv validate -s sarif-schema-2.1.0.json -d results.sarif

# Python
pip install jsonschema
```

```python
from jsonschema import validate, ValidationError
import json

def validate_sarif(sarif_path: str, schema_path: str) -> bool:
    with open(sarif_path) as f:
        sarif = json.load(f)
    with open(schema_path) as f:
        schema = json.load(f)
    try:
        validate(sarif, schema)
        return True
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif

- name: Check for high severity
  run: |
    HIGH_COUNT=$(jq '[.runs[].results[] | select(.level == "error")] | length' results.sarif)
    if [ "$HIGH_COUNT" -gt 0 ]; then
      echo "Found $HIGH_COUNT high severity issues"
      exit 1
    fi
```

### Regression Detection

```python
from sarif import loader

def check_for_regressions(baseline: str, current: str) -> int:
    baseline_fps = {get_fingerprint(r) for r in loader.load_sarif_file(baseline).get_results()}
    new_issues = [r for r in loader.load_sarif_file(current).get_results()
                  if get_fingerprint(r) not in baseline_fps]
    return len(new_issues)
```

## Key Principles

1. **Validate first** — check SARIF structure before processing
2. **Handle optionals** — many fields are optional; use defensive access
3. **Normalize paths** — tools report paths differently; normalize early
4. **Fingerprint wisely** — combine multiple strategies for stable deduplication
5. **Stream large files** — use ijson for 100MB+ files
6. **Aggregate thoughtfully** — preserve tool metadata when combining files

## Resources

- [jq query templates]({baseDir}/resources/jq-queries.md) — 40+ queries for common SARIF operations
- [Python utilities]({baseDir}/resources/sarif_helpers.py) — normalize, fingerprint, deduplicate helpers
- [OASIS SARIF 2.1.0 Spec](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [Microsoft SARIF Tutorials](https://github.com/microsoft/sarif-tutorials)
- [sarif-tools (Python)](https://github.com/microsoft/sarif-tools)
- [GitHub SARIF Support](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)

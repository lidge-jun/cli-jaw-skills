import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


batch = load_module(
    "officecli_dataframe_to_batch",
    ROOT / "officecli-data-pipeline" / "scripts" / "dataframe_to_batch.py",
)
verify = load_module(
    "officecli_verify_persisted_cells",
    ROOT / "officecli-data-pipeline" / "scripts" / "verify_persisted_cells.py",
)


def test_batch_commands_preserve_cjk_newlines_and_numbers():
    payload = {
        "columns": ["제목", "내용", "금액"],
        "data": [["점검", "첫 줄\n둘째 줄", 120000], ["빈 값", None, 0.5]],
    }
    commands = batch.commands_for_split_payload("Slack 캡처 정리", payload)

    by_path = {item["path"]: item["props"] for item in commands}
    assert by_path["/Slack 캡처 정리/A1"] == {"value": "제목"}
    assert by_path["/Slack 캡처 정리/B2"] == {"value": "첫 줄\n둘째 줄"}
    assert by_path["/Slack 캡처 정리/C2"] == {
        "value": "120000",
        "type": "number",
    }
    assert "/Slack 캡처 정리/B3" not in by_path
    assert by_path["/Slack 캡처 정리/C3"] == {
        "value": "0.5",
        "type": "number",
    }


def test_batch_commands_reject_ragged_rows():
    try:
        batch.commands_for_split_payload(
            "Sheet1", {"columns": ["a", "b"], "data": [["only-one"]]}
        )
    except ValueError as error:
        assert "expected 2" in str(error)
    else:
        raise AssertionError("ragged rows must fail")


def test_fixture_converts_to_explicit_cells_without_losing_newline():
    fixture = ROOT / "tests" / "fixtures" / "officecli-data-pipeline"
    commands = batch.load_commands([f"Sheet1={fixture / 'cjk-multiline.split.json'}"])
    by_path = {item["path"]: item["props"] for item in commands}

    assert len(commands) == 9
    assert by_path["/Sheet1/B2"]["value"] == "첫 줄\n둘째 줄"
    assert by_path["/Sheet1/C2"] == {"value": "120000", "type": "number"}


def test_persisted_readback_requires_exact_values():
    responses = {
        "/Sheet1/A1": {"matches": 1, "text": "거래처"},
        "/Sheet1/B2": {"data": {"value": "첫 줄\n둘째 줄"}},
    }

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(
            command, 0, stdout=json.dumps(responses[command[3]], ensure_ascii=False), stderr=""
        )

    checked = verify.verify_cells(
        "report.xlsx",
        {"/Sheet1/A1": "거래처", "/Sheet1/B2": "첫 줄\n둘째 줄"},
        run=fake_run,
    )
    assert checked == [
        ("/Sheet1/A1", "거래처"),
        ("/Sheet1/B2", "첫 줄\n둘째 줄"),
    ]


def test_persisted_readback_rejects_empty_skeleton():
    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(
            command, 0, stdout='{"matches":1,"text":"(empty)"}', stderr=""
        )

    try:
        verify.verify_cells(
            "report.xlsx", {"/Sheet1/A1": "expected header"}, run=fake_run
        )
    except RuntimeError as error:
        assert "persisted value mismatch" in str(error)
        assert "(empty)" in str(error)
    else:
        raise AssertionError("an empty persisted cell must fail verification")


def test_skill_primary_path_uses_file_batch_close_and_readback():
    skill = (ROOT / "officecli-data-pipeline" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    primary = skill.split("## Legacy CSV Import (Opt-in Only)", 1)[0]

    assert "\nofficecli import " not in primary
    assert "officecli batch sales_report.xlsx --input sales_report.data.json" in primary
    assert "officecli close sales_report.xlsx" in primary
    assert "python scripts/verify_persisted_cells.py sales_report.xlsx" in primary


@pytest.mark.officecli
def test_real_officecli_safe_batch_roundtrip(tmp_path):
    officecli = os.environ.get("OFFICECLI_BIN") or shutil.which("officecli")
    if not officecli:
        pytest.skip("OFFICECLI_BIN/officecli is not available")

    fixture = ROOT / "tests" / "fixtures" / "officecli-data-pipeline"
    commands = batch.load_commands([f"Sheet1={fixture / 'cjk-multiline.split.json'}"])
    commands_path = tmp_path / "commands.json"
    commands_path.write_text(
        json.dumps(commands, ensure_ascii=False), encoding="utf-8"
    )
    workbook = tmp_path / "roundtrip.xlsx"

    for args in (
        ["create", str(workbook), "--json"],
        ["batch", str(workbook), "--input", str(commands_path), "--json"],
        ["close", str(workbook), "--json"],
    ):
        result = subprocess.run(
            [officecli, *args], capture_output=True, text=True, encoding="utf-8"
        )
        assert result.returncode == 0, result.stderr

    expectations = json.loads(
        (fixture / "cjk-multiline.expect.json").read_text(encoding="utf-8")
    )
    assert verify.verify_cells(str(workbook), expectations, officecli=officecli) == list(
        expectations.items()
    )

    validation = subprocess.run(
        [officecli, "validate", str(workbook), "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert validation.returncode == 0, validation.stderr
    assert json.loads(validation.stdout)["success"] is True

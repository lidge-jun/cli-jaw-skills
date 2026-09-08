"""CJK regression tests — Korean, Japanese, Chinese roundtrips across all formats."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import run_officecli, run_officecli_json


@pytest.mark.cjk
@pytest.mark.officecli
class TestCJKDocxRoundtrip:
    """DOCX CJK text roundtrip tests."""

    def test_korean_docx(self, tmp_docx: Path) -> None:
        """Korean: create → add → validate → view → assert preserved."""
        text = "서울특별시 강남구 테헤란로"
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", f"text={text}")

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        view = run_officecli("view", str(tmp_docx), "text")
        assert text in view.stdout

    def test_japanese_docx(self, tmp_docx: Path) -> None:
        """Japanese: create → add → validate."""
        text = "東京都渋谷区神宮前"
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", f"text={text}")

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        view = run_officecli("view", str(tmp_docx), "text")
        assert text in view.stdout

    def test_chinese_docx(self, tmp_docx: Path) -> None:
        """Chinese: create → add → validate."""
        text = "北京市朝阳区建国门外大街"
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", f"text={text}")

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        view = run_officecli("view", str(tmp_docx), "text")
        assert text in view.stdout

    def test_mixed_languages_docx(self, tmp_docx: Path) -> None:
        """Mixed English + Korean in same document."""
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", "text=Hello World")
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", "text=안녕하세요 세계")
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", "text=Goodbye 잘가요")

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        view = run_officecli("view", str(tmp_docx), "text")
        assert "Hello World" in view.stdout
        assert "안녕하세요 세계" in view.stdout
        assert "Goodbye 잘가요" in view.stdout

    def test_korean_long_text_docx(self, tmp_docx: Path) -> None:
        """Long Korean paragraph with mixed punctuation."""
        text = "대한민국은 민주공화국이다. 대한민국의 주권은 국민에게 있고, 모든 권력은 국민으로부터 나온다."
        run_officecli("add", str(tmp_docx), "/body",
                      "--type", "paragraph", "--prop", f"text={text}")

        val = run_officecli_json("validate", str(tmp_docx))
        assert val["success"] is True

        view = run_officecli("view", str(tmp_docx), "text")
        assert "대한민국은 민주공화국이다" in view.stdout


@pytest.mark.cjk
@pytest.mark.officecli
class TestCJKPptxRoundtrip:
    """PPTX CJK text roundtrip tests."""

    def test_korean_pptx(self, tmp_pptx: Path) -> None:
        """Korean PPTX: create → add slide → add Korean shape → validate → view → assert."""
        text = "한국어 프레젠테이션 제목입니다"
        run_officecli("add", str(tmp_pptx), "/", "--type", "slide")
        run_officecli("add", str(tmp_pptx), "/slide[1]",
                      "--type", "shape",
                      "--prop", "type=textbox",
                      "--prop", f"text={text}")

        val = run_officecli_json("validate", str(tmp_pptx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        view = run_officecli("view", str(tmp_pptx), "text")
        assert text in view.stdout

    def test_japanese_pptx(self, tmp_pptx: Path) -> None:
        """Japanese PPTX roundtrip."""
        text = "日本語のプレゼンテーション"
        run_officecli("add", str(tmp_pptx), "/", "--type", "slide")
        run_officecli("add", str(tmp_pptx), "/slide[1]",
                      "--type", "shape",
                      "--prop", "type=textbox",
                      "--prop", f"text={text}")

        val = run_officecli_json("validate", str(tmp_pptx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        view = run_officecli("view", str(tmp_pptx), "text")
        assert text in view.stdout

    def test_chinese_pptx(self, tmp_pptx: Path) -> None:
        """Chinese PPTX roundtrip."""
        text = "中文演示文稿"
        run_officecli("add", str(tmp_pptx), "/", "--type", "slide")
        run_officecli("add", str(tmp_pptx), "/slide[1]",
                      "--type", "shape",
                      "--prop", "type=textbox",
                      "--prop", f"text={text}")

        val = run_officecli_json("validate", str(tmp_pptx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        view = run_officecli("view", str(tmp_pptx), "text")
        assert text in view.stdout


@pytest.mark.cjk
@pytest.mark.officecli
class TestCJKXlsxRoundtrip:
    """XLSX CJK text roundtrip tests."""

    def test_korean_xlsx(self, tmp_xlsx: Path) -> None:
        """CJK text in Excel cells should round-trip together."""
        run_officecli("set", str(tmp_xlsx), "/Sheet1/A1", "--prop", "value=이름")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/B1", "--prop", "value=나이")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/A2", "--prop", "value=홍길동")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/B2", "--prop", "value=25")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/C1", "--prop", "value=住所")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/C2", "--prop", "value=東京都渋谷区神宮前")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/D1", "--prop", "value=地址")
        run_officecli("set", str(tmp_xlsx), "/Sheet1/D2", "--prop", "value=北京市朝阳区建国门外大街")

        val = run_officecli_json("validate", str(tmp_xlsx))
        assert val["success"] is True
        assert val["data"]["count"] == 0

        view = run_officecli("view", str(tmp_xlsx), "text")
        assert "이름" in view.stdout
        assert "홍길동" in view.stdout
        assert "住所" in view.stdout
        assert "東京都渋谷区神宮前" in view.stdout
        assert "地址" in view.stdout
        assert "北京市朝阳区建国门外大街" in view.stdout

---
name: pdf-vision
description: >
  Read and analyze PDFs combining perfect visual layout (image rendering) with high-fidelity text extraction to prevent OCR errors.
  Triggers: "pdf", "기출문제", "표", "수식 포함 pdf", "이미지로 변환", "pdf 읽기", "pdf 추출", "pdf-vision"
---
# PDF Vision Skill

## Goal
To give AI agents the ability to read and solve complex PDF documents (like exams, charts, and tables) by providing both a high-resolution image for visual context and exact text for content accuracy via a hybrid python script.

## Quick Reference

| I need...                     | Command                                                                    |
| ----------------------------- | -------------------------------------------------------------------------- |
| Extract Image + Text from PDF | `python3 <skill>/scripts/pdf_hybrid_extract.py "<file.pdf>" <page_number>` |

Replace `<skill>` with the absolute path to this skill folder.

## Instructions

### 0. Pre-flight (every invocation)
```bash
# Ensure dependencies exist (run from workspace root)
python3 -c "import pypdf, pypdfium2" 2>/dev/null \
  || python3 -m pip install pypdf pypdfium2 -q
```

### 1. Extract (`pdf_hybrid_extract.py`)
1. **Locate the PDF file**: Identify the absolute path of the target PDF file.
2. **Determine the page**: Identify which page (1-based index) needs to be analyzed.
3. **Run the extraction script**: Execute the script in a shell to generate both the image and the text.
   ```bash
   python3 .agents/skills/pdf-vision/scripts/pdf_hybrid_extract.py "/absolute/path/to/file.pdf" <page_number>
   ```
4. **Read the Image**: The script outputs a file path for the rendered PNG (e.g., `/absolute/path/to/file_pdf/page_1.png`). Open this image file to visually analyze it.
5. **Analyze holistically**: Combine the visual layout/tables from the image with the exact text printed in the script's stdout to accurately answer the user's request.

### 2. Bulk Solving via Sub-agents & Legal Revisions
If the user asks to solve an entire page or exam:
1. **Extract Image & Text** as shown above.
2. **Legal Revision Check (CRITICAL)**: If the document contains accounting standards, corporate law, or tax law (회계기준, 상법, 세법 등), you MUST trigger the **`search` skill** (by following its instructions or using triggers like "검색", "search") to thoroughly check if there have been any recent law revisions. **Acknowledge that the current year is 2026**, so you must search for revisions up to 2026 (e.g., "2025 상법 개정", "2026 세법 개정"). You must follow the `search` skill's strict rules (dual-tool verification, confidence tagging, citation) and state these revisions explicitly in your answer if they impact the outcome compared to the time the test was taken.
3. **Top-Down & Proximate Concept Explanation**: When explaining a multiple-choice question, use a structured, top-down approach to help the user study and review efficiently. For *every single option (선지)*, provide the explanation in a structured format:
   - **[N]번 선지**: [핵심 개념명]
   - **관련 개념**: [해당 개념에 대한 상세한 설명 및 **근접 관련 개념들(Proximate Concepts)의 총체적 확장**. 단순히 선지에 나온 단어만 설명하지 말고, 해당 이론의 전체 구조나 맞닿아 있는 파생 개념(예: 켈리의 귀인 모형에서 '일관성'이 나오면 '합의성', '특이성' 및 그에 따른 내/외적 귀인 결과표까지)을 모두 포괄하여 **분량이 길어지더라도 아주 상세하게** 설명할 것]
   - **결론**: [해당 선지가 왜 맞거나 틀린 지 명확한 이유]
4. **Spawn Sub-agents**: Do not try to solve 10 questions in a single response. Spawn a separate sub-agent for each question (or batch of 2-3 questions) to analyze the provided PNG and Text, and return the detailed solution taking into account any found revisions.
5. **Provide Context**: Pass the `page_N.png` file path, the extracted text, and the revision search results to each sub-agent.
6. **Compile Results**: Gather the answers from the sub-agents and present them to the user.

### 3. Answer Verification
- The official answer key is typically located alongside the exam PDF. 
- Example path: `/Users/jun/Developer/new/회계사 기출문제/25년 공인회계사 1차 문제 및 가답안/정답_2025.pdf`
- You can use this skill on the answer key PDF (or just `view_file` if it's pure text) to verify the solved answers before presenting them to the user.

## Constraints
- **1-indexed**: Pages are 1-indexed (first page is 1).
- **Image Analysis**: Open the generated PNG to analyze the page. Do NOT attempt to open the original PDF as an image.
- **Fallback**: If the PDF is scanned or has no embedded text, the script prints a notice (`No embedded text found`). Rely completely on image vision in this case.

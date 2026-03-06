# PDF Vision Skill Rules

1. Use `pdf_hybrid_extract.py` to extract both text and a rendered PNG.
2. Read the image using `view_file` to understand the layout and tables.
3. Read the extracted text from stdout for 100% exact copy to prevent OCR hallucinations.
4. Always prioritize combining both for solving visual exam questions.

import sys
import json
import argparse
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print(json.dumps({"error": "pdfplumber not installed. Run: pip install pdfplumber"}), file=sys.stderr)
    sys.exit(1)

def check_pdf(pdf_path, text_threshold=100, quality_ratio=0.3):
    """
    Analyzes a PDF to determine which pages have sufficient text and which need OCR.
    Args:
        pdf_path: Path to the PDF file.
        text_threshold: Minimum number of characters to consider a page 'text-based'.
        quality_ratio: Minimum ratio of unique meaningful lines to total lines (0.0~1.0).
                       Filters out pages with only boilerplate headers/footers/URLs.
    """
    path = Path(pdf_path)
    if not path.exists():
        print(json.dumps({"error": f"File not found: {pdf_path}"}), file=sys.stderr)
        sys.exit(1)

    result = {
        "file": str(path.absolute()),
        "total_pages": 0,
        "text_pages": [],  # Pages that have enough text
        "ocr_pages": []    # Pages that need Vision OCR
    }

    try:
        with pdfplumber.open(str(path)) as pdf:
            result["total_pages"] = len(pdf.pages)
            
            for i, page in enumerate(pdf.pages):
                page_num = i + 1
                text = page.extract_text()
                
                # CID 폰트 매핑 실패 시 null byte만 반환 → 제거
                if text:
                    text = text.replace("\x00", "").strip()
                
                is_text_page = False
                if text and len(text) >= text_threshold:
                    # Quality check: filter boilerplate-only pages
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    if lines:
                        # Count lines that are NOT just URLs, page numbers, or short headers
                        meaningful = [l for l in lines 
                                      if len(l) > 15 
                                      and not l.startswith('http') 
                                      and not l.replace('/', '').replace(' ', '').isdigit()]
                        ratio = len(meaningful) / len(lines) if lines else 0
                        is_text_page = ratio >= quality_ratio
                
                if is_text_page:
                    result["text_pages"].append({
                        "page": page_num,
                        "text": text
                    })
                else:
                    result["ocr_pages"].append(page_num)
                    
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check PDF for text vs image pages")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--threshold", type=int, default=100, 
                        help="Text character threshold. Below this = OCR needed (default: 100)")
    parser.add_argument("--quality-ratio", type=float, default=0.3,
                        help="Min ratio of meaningful lines to total lines (default: 0.3)")
    
    args = parser.parse_args()
    check_pdf(args.pdf_path, args.threshold, args.quality_ratio)

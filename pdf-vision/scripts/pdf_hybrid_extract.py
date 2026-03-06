import sys
import os
import subprocess

def install_deps():
    try:
        import pypdf
        import pypdfium2
    except ImportError:
        print("Installing dependencies: pypdf pypdfium2...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf", "pypdfium2", "-q"])

install_deps()

from pypdf import PdfReader
import pypdfium2 as pdfium

def main():
    if len(sys.argv) < 3:
        print("Usage: python pdf_hybrid_extract.py <pdf_path> <page_number_1_based>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    
    try:
        page_num = int(sys.argv[2])
    except ValueError:
        print("Error: Page number must be an integer.")
        sys.exit(1)
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
        
    # 0. Page count & validation via pypdf (needed by both steps)
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        sys.exit(1)

    if page_num < 1 or page_num > total_pages:
        print(f"Error: Invalid page number. Total pages: {total_pages}")
        sys.exit(1)

    # 1. Text extraction via pypdf (non-fatal — image rendering can proceed)
    try:
        page = reader.pages[page_num - 1]
        text_content = page.extract_text() or ""
    except Exception as e:
        print(f"Warning: Text extraction failed: {e}")
        text_content = ""

    # 2. Image rendering via pypdfium2
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        page_pdfium = pdf[page_num - 1]
        
        # rendering to image. scale=3 is usually enough for 300 DPI readability
        bitmap = page_pdfium.render(scale=3)
        pil_image = bitmap.to_pil()
        
        # Save to a subfolder next to the original PDF
        base_dir = os.path.dirname(pdf_path)
        pdf_filename = os.path.basename(pdf_path)
        pdf_name_no_ext = os.path.splitext(pdf_filename)[0]
        
        out_dir = os.path.join(base_dir, pdf_name_no_ext)
        os.makedirs(out_dir, exist_ok=True)
        
        img_filename = f"page_{page_num}.png"
        img_path = os.path.join(out_dir, img_filename)
        pil_image.save(img_path)
    except Exception as e:
        print(f"Error extracting image: {e}")
        sys.exit(1)
        
    print("================ HYBRID EXTRACTION RESULT ================")
    print(f"📄 Target PDF: {pdf_path}")
    print(f"📄 Page: {page_num} of {total_pages}")
    print(f"")
    print(f"🖼️ [1] Rendered Image Path (Use view_file to visually analyze):")
    print(f"{img_path}")
    print(f"")
    print(f"📝 [2] Extracted Text (Use for precise content matching to prevent OCR typos):")
    print("--- TEXT START ---")
    if text_content.strip():
        print(text_content.strip())
    else:
        print("(No embedded text found — rely on image vision for this page.)")
    print("--- TEXT END ---")

if __name__ == "__main__":
    main()

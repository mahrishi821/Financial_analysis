import fitz  # PyMuPDF
import tempfile
import subprocess
import os
import pythoncom
from pathlib import Path
import win32com.client
from concurrent.futures import ThreadPoolExecutor, as_completed
from docx2pdf import convert

class DocumentParaphraser:
    def _ocr_single_page(self, doc, page_num, temp_dir):
        """Run OCRmyPDF --force-ocr on a single page and return the text."""
        single_page_path = os.path.join(temp_dir, f"page_{page_num}.pdf")
        processed_page_path = os.path.join(temp_dir, f"page_{page_num}_ocr.pdf")

        # Extract single page
        single_doc = fitz.open()
        single_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        single_doc.save(single_page_path)
        single_doc.close()

        # Force OCR
        subprocess.run(
            ["ocrmypdf", "--force-ocr", single_page_path, processed_page_path],
            check=True, capture_output=True
        )

        # Extract text
        processed_doc = fitz.open(processed_page_path)
        ocr_text = processed_doc[0].get_text().strip()
        processed_doc.close()

        return page_num, ocr_text

    def _convert_docx_to_pdf(self, docx_data):
        """Convert DOCX bytes or BytesIO to PDF bytes using Microsoft Word COM automation (Windows only)."""

        # Handle BytesIO or bytes
        if hasattr(docx_data, "read"):
            docx_data = docx_data.read()

        # Save temp DOCX file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
            temp_docx.write(docx_data)
            docx_path = Path(temp_docx.name)

        pdf_path = docx_path.with_suffix(".pdf")

        try:
            # Initialize COM for the current thread
            pythoncom.CoInitialize()

            # Open Word and convert DOCX → PDF
            word = win32com.client.DispatchEx("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(str(docx_path))
            doc.SaveAs(str(pdf_path), FileFormat=17)  # 17 = PDF
            doc.Close()
            word.Quit()

            # Read PDF bytes
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

        finally:
            # Cleanup COM and temp files
            pythoncom.CoUninitialize()
            if docx_path.exists():
                os.remove(docx_path)
            if pdf_path.exists():
                os.remove(pdf_path)

        return pdf_bytes

    def extract_text_from_docx(self, file_bytes) -> str:
        """Convert DOCX to PDF and extract text with OCR when needed."""
        pdf_bytes = self._convert_docx_to_pdf(file_bytes)
        text_results = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            ocr_pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text().strip()
                images = page.get_images(full=True)

                if page_text and not images:
                    # Text-only page — store directly
                    text_results[page_num] = page_text
                else:
                    # Mixed or image-only page — needs OCR
                    ocr_pages.append(page_num)

            # Process OCR pages in parallel
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                futures = [
                    executor.submit(self._ocr_single_page, doc, p, temp_dir)
                    for p in ocr_pages
                ]
                for future in as_completed(futures):
                    page_num, ocr_text = future.result()
                    text_results[page_num] = ocr_text

            doc.close()

        # Combine results in correct order
        final_text = "\n".join(text_results[p] for p in sorted(text_results.keys()))
        return final_text

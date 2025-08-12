import fitz  # PyMuPDF
import tempfile
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


class Paraphrasepdf:

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

    def extract_text_from_pdf(self, file_bytes) -> str:
        text_results = {}
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        # Create one temp directory for all OCR files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Identify pages needing OCR
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
                futures = [executor.submit(self._ocr_single_page, doc, p, temp_dir) for p in ocr_pages]
                for future in as_completed(futures):
                    page_num, ocr_text = future.result()

                    # Fallback: If OCR text is empty, try original extraction
                    if not ocr_text:
                        ocr_text = doc[page_num].get_text().strip()

                    text_results[page_num] = ocr_text

        doc.close()

        # Combine results in correct order
        final_text = "\n".join(text_results[p] for p in sorted(text_results.keys()))
        return final_text

import os
from common.utils.doc_paraphraser import DocumentParaphraser
from common.utils.pdf_paraphraser import Paraphrasepdf
from common.utils.excel_pharaphraser import ExcelDataProcessor


class FileTextExtractor:
    """
    Utility class to extract text from various document formats.
    Supports: PDF, Excel (.xls, .xlsx), Word (.doc, .docx).
    """

    SUPPORTED_TYPES = {
        ".pdf": "pdf",
        ".xls": "excel",
        ".xlsx": "excel",
        ".doc": "docx",
        ".docx": "docx",
    }

    def __init__(self):
        # Initialize processors only once
        self.pdf_processor = Paraphrasepdf()
        self.excel_processor = ExcelDataProcessor()
        self.doc_processor = DocumentParaphraser()

    def extract(self, file_path: str, file_bytes: bytes):
        """
        Extract text from a file.
        Args:
            file_path (str): Path to the uploaded file.
            file_bytes (bytes): Raw file content in bytes.
        Returns:
            tuple: (extracted_text: str, file_type: str)
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return self._extract_pdf(file_bytes), "pdf"

        elif ext in [".xls", ".xlsx"]:
            return self._extract_excel(file_path), "excel"

        elif ext in [".doc", ".docx"]:
            return self._extract_docx(file_bytes), "docx"

        return "", "unknown"

    def _extract_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF bytes."""
        return self.pdf_processor.extract_text_from_pdf(file_bytes)

    def _extract_excel(self, file_path: str) -> str:
        """Extract text from Excel file path."""
        return self.excel_processor.extract_text_from_excel(file_path)

    def _extract_docx(self, file_bytes: bytes) -> str:
        """Extract text from Word document bytes."""
        return self.doc_processor.extract_text_from_docx(file_bytes)

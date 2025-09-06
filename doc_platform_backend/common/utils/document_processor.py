import os
from .doc_paraphraser import DocumentParaphraser
from .pdf_paraphraser import Paraphrasepdf
from .excel_pharaphraser import ExcelDataProcessor
# from .finance_classifire import FinancialTextClassifier


class FileTextExtractor:
    """Class to extract text from different file types."""

    def __init__(self):
        self.supported_types = {
            ".pdf": self._extract_pdf,
            ".xls": self._extract_excel,
            ".xlsx": self._extract_excel,
            ".doc": self._extract_docx,
            ".docx": self._extract_docx,
        }

    def extract(self, file_path: str, file_bytes: bytes):
        """
        Extract text from a given file.

        Args:
            file_path (str): Path or name of the file.
            file_bytes (bytes): File content in bytes (needed for PDF, DOCX).

        Returns:
            tuple: (extracted_text: str, file_type: str)
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext in self.supported_types:
            return self.supported_types[ext](file_path, file_bytes)
        return "", "unknown"

    def _extract_pdf(self, file_path, file_bytes):
        pdf = Paraphrasepdf()
        text = pdf.extract_text_from_pdf(file_bytes)
        return text, "pdf"

    def _extract_excel(self, file_path, file_bytes=None):
        ex = ExcelDataProcessor()
        text = ex.extract_text_from_excel(file_path)
        return text, "excel"

    def _extract_docx(self, file_path, file_bytes):
        doc = DocumentParaphraser()
        text = doc.extract_text_from_docx(file_bytes)
        return text, "docx"

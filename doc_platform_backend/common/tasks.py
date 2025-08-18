# bronze/tasks.py
import zipfile
import os
import mimetypes
from django.conf import settings
from documents.models import DocumentUpload, ExtractedDocument


@shared_task
def process_uploaded_zip(upload_id):
    try:
        upload = DocumentUpload.objects.get(id=upload_id)
        upload.status = "extracted"
        upload.save(update_fields=["status"])

        extract_dir = os.path.join(settings.MEDIA_ROOT, f"bronze/{upload.company.id}/extracted/{upload.id}")
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(upload.zip_file.path, "r") as zf:
            zf.extractall(extract_dir)

        for file_name in os.listdir(extract_dir):
            file_path = os.path.join(extract_dir, file_name)
            file_type = mimetypes.guess_type(file_path)[0] or "unknown"

            ExtractedDocument.objects.create(
                upload=upload,
                file_name=file_name,
                file_path=file_path,
                file_type=file_type,
                preview_text=None  # optional: run OCR/parser later
            )

        upload.status = "processed"
        upload.save(update_fields=["status"])
        return f"Upload {upload_id} processed successfully."

    except Exception as e:
        upload = DocumentUpload.objects.get(id=upload_id)
        upload.status = "failed"
        upload.error_log = str(e)
        upload.save(update_fields=["status", "error_log"])
        raise

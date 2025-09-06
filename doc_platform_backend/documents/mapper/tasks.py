# mapper/tasks.py
# from celery import shared_task
from ..models import StructuredDocument, Annexure, AuditLog, SheetUnit
import json

# @shared_task
def task_process_chunk(chunk_payload):
    # chunk_payload: dict with header, rows, metadata
    # Build prompt to call LLM (include schema definition, chunk index)
    # Call LLM to map rows -> JSON chunk
    # Save chunk output to temporary storage (Redis or DB table). For brevity, write to AuditLog
    AuditLog.objects.create(sheet_unit_id=chunk_payload["sheet_id"],
                            action="chunk_mapped",
                            details={"chunk_index": chunk_payload["chunk_index"], "mapped_len": len(chunk_payload["rows"])})
    # After mapping all chunks, a separate orchestrator should call merge_chunks
    return {"status":"ok"}

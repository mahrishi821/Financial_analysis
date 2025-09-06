# chunker/tasks.py
from celery import shared_task
from ..models import SheetUnit, StructuredDocument, Annexure, AuditLog
import math

MAX_ROWS_FOR_SINGLE_CALL = 400
CHUNK_ROWS = 300
OVERLAP = 2

# @shared_task
def task_process_sheet(sheet_unit_id):
    sheet = SheetUnit.objects.get(id=sheet_unit_id)
    # get raw table
    raw = sheet.raw_table
    # if pointer -> read CSV from storage (not shown)
    # assume raw_table is a list for simplicity
    if isinstance(raw, dict) and raw.get("csv_pointer"):
        # load CSV from storage (omitted here) -> df_rows
        df_rows = load_csv_from_storage(raw["csv_pointer"])
    else:
        df_rows = raw or []

    row_count = sheet.row_count or len(df_rows)
    if row_count <= MAX_ROWS_FOR_SINGLE_CALL:
        # send full sheet to schema_mapper
        result = schema_map_full(sheet, df_rows)
        persist_mapped_result(sheet, result)
    else:
        # chunk
        chunks = []
        header = sheet.header_rows or []
        start = 0
        while start < row_count:
            end = min(start + CHUNK_ROWS, row_count)
            chunk_rows = df_rows[start:end]
            chunks.append({
                "sheet_id": str(sheet.id),
                "chunk_index": len(chunks),
                "start": start,
                "end": end,
                "header": header,
                "rows": chunk_rows,
                "total_chunks": None  # fill later
            })
            start = end - OVERLAP  # overlap to keep continuity
        total = len(chunks)
        for c in chunks:
            c["total_chunks"] = total
            # enqueue chunk processing
            from mapper.tasks import task_process_chunk
            task_process_chunk(c)
        AuditLog.objects.create(sheet_unit=sheet, action="chunks_created", details={"total_chunks": total})

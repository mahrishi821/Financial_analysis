# import json
# import io
# import uuid
# import tempfile
# import os
# import subprocess
# import pandas as pd
# import fitz  # PyMuPDF
# from PIL import Image
# from openpyxl import load_workbook
# from django.core.files.storage import default_storage
# from documents.models import UploadedFile, SheetUnit, AuditLog
# from ..classifier.tasks import rule_based_classify
#
# MAX_INLINE_ROWS = 300  # threshold for saving raw_table inline vs csv pointer
# CHUNK_ROWS = 200
#
#
# # -------------------------------
# # 🔹 Header detection with context
# # -------------------------------
# def detect_header_and_samples(df, max_header_search=15, sample_limit=20, max_header_rows=2):
#     """
#     Detects header rows and sample rows in a dataframe using heuristics.
#     Also returns pre-header context (rows above detected header).
#     """
#     row_count, col_count = df.shape
#     non_empty_rows = [i for i in range(row_count) if df.iloc[i].notna().any()]
#
#     if not non_empty_rows:
#         return [], [], []
#
#     def score_row(row_idx):
#         values = [str(v).strip() for v in df.iloc[row_idx].tolist()]
#         non_empty = sum(1 for v in values if v)
#         text_like = sum(1 for v in values if v.isalpha())
#         num_like = sum(1 for v in values if v.replace(".", "", 1).isdigit())
#         return non_empty + text_like - num_like
#
#     # Step 1: score first N rows
#     candidates = non_empty_rows[:max_header_search]
#     scores = {r: score_row(r) for r in candidates}
#     header_row_idx = max(scores, key=scores.get)
#
#     # Step 2: allow multi-row headers
#     header_rows = [list(df.iloc[header_row_idx].tolist())]
#     if max_header_rows > 1 and (header_row_idx + 1 < row_count):
#         next_score = score_row(header_row_idx + 1)
#         if next_score >= scores[header_row_idx] * 0.7:  # threshold heuristic
#             header_rows.append(list(df.iloc[header_row_idx + 1].tolist()))
#
#     # Step 3: pre-header context = non-empty rows before detected header
#     pre_header_context = [
#         list(df.iloc[r].tolist())
#         for r in non_empty_rows
#         if r < header_row_idx
#     ]
#
#     # Step 4: collect sample rows after headers
#     last_header_row = header_row_idx + len(header_rows) - 1
#     sample_rows = [
#         list(df.iloc[r].tolist())
#         for r in non_empty_rows
#         if r > last_header_row
#     ][:sample_limit]
#
#     return header_rows, sample_rows, pre_header_context
#
#
# def task_extract_workbook(uploaded_file_id):
#     uploaded = UploadedFile.objects.get(file_id=uploaded_file_id)
#     file_obj = uploaded.s3_path
#
#     # Step 1: Try loading Excel with pandas
#     try:
#         xls = pd.ExcelFile(file_obj)
#     except Exception as e:
#         AuditLog.objects.create(sheet_unit=None, action="extract_error", details={"error": str(e)})
#         raise
#
#     # Step 2: Also open with openpyxl for charts/images
#     try:
#         wb = load_workbook(file_obj)
#     except Exception as e:
#         wb = None
#         AuditLog.objects.create(sheet_unit=None, action="openpyxl_error", details={"error": str(e)})
#
#     for sheet_name in xls.sheet_names:
#         # --- Extract raw table ---
#         df = xls.parse(sheet_name, header=None, dtype=str).fillna("")
#         row_count, col_count = df.shape
#
#         # ✅ Use new detection with pre_header_context
#         header_rows, sample_rows, pre_header_context = detect_header_and_samples(df)
#
#         # Decide whether to embed raw_table or save CSV
#         if row_count <= MAX_INLINE_ROWS:
#             raw_table = df.values.tolist()
#         else:
#             tmp_csv = io.StringIO()
#             df.to_csv(tmp_csv, index=False, header=False)
#             csv_bytes = tmp_csv.getvalue().encode()
#             object_name = f"uploaded_raw_tables/{uploaded.file_id}/{uuid.uuid4()}.csv"
#             default_storage.save(object_name, io.BytesIO(csv_bytes))
#             raw_table = {"csv_pointer": object_name}
#
#         # --- Extract metadata: charts + images (if available) ---
#         charts_info, ocr_results = {}, {}
#         if wb:
#             ws = wb[sheet_name]
#             charts_info[sheet_name] = len(getattr(ws, "_charts", []))
#             extracted_texts = []
#             for img in getattr(ws, "_images", []):
#                 try:
#                     img_bytes = img._data()
#                     image = Image.open(io.BytesIO(img_bytes))
#                     with tempfile.TemporaryDirectory() as tmp_dir:
#                         pdf_path = os.path.join(tmp_dir, "img.pdf")
#                         ocr_pdf_path = os.path.join(tmp_dir, "img_ocr.pdf")
#                         image.convert("RGB").save(pdf_path)
#
#                         subprocess.run(
#                             ["ocrmypdf", "--force-ocr", pdf_path, ocr_pdf_path],
#                             check=True, capture_output=True
#                         )
#
#                         doc = fitz.open(ocr_pdf_path)
#                         ocr_text = "\n".join([page.get_text().strip() for page in doc])
#                         doc.close()
#
#                         if ocr_text.strip():
#                             extracted_texts.append(ocr_text.strip())
#                 except Exception as e:
#                     extracted_texts.append(f"[OCR Error: {str(e)}]")
#
#             if extracted_texts:
#                 ocr_results[sheet_name] = extracted_texts
#
#         metadata = {
#             "charts": charts_info,
#             "ocr_from_images": ocr_results,
#             "pre_header_context": pre_header_context
#         }
#
#         # --- Save to DB ---
#         sheet_unit = SheetUnit.objects.create(
#             uploaded_file=uploaded,
#             sheet_name=sheet_name,
#             row_count=row_count,
#             col_count=col_count,
#             header_rows=header_rows,
#             sample_rows=sample_rows,
#             raw_table=raw_table,
#             metadata=metadata
#         )
#         AuditLog.objects.create(
#             sheet_unit=sheet_unit,
#             action="sheet_extracted",
#             details={
#                 "rows": row_count,
#                 "cols": col_count,
#                 "charts": charts_info.get(sheet_name, 0),
#                 "header_detected": header_rows[:2],
#                 "pre_header_count": len(pre_header_context)
#             }
#         )
#         # from django.forms.models import model_to_dict
#         # print(f"Sheet Unit : {json.dumps(model_to_dict(sheet_unit), indent=2, default=str)}")
#
#         rule_based_classify(header_rows,sample_rows,metadata["pre_header_context"])
#

import json
import io
import uuid
import tempfile
import os
import subprocess
import pandas as pd
import fitz  # PyMuPDF
import numpy as np
from PIL import Image
from openpyxl import load_workbook
from django.core.files.storage import default_storage
from documents.models import UploadedFile, SheetUnit, AuditLog
from ..classifier.tasks import rule_based_classify

MAX_INLINE_ROWS = 300
CHUNK_ROWS = 200


# ------------------------------------------------
# 🔹 2D Table Detector with Gap Tolerance + Headers
# ------------------------------------------------
def detect_tables_2d(df, max_header_search=15, sample_limit=20,
                     max_header_rows=3, min_block_size=5, gap_tolerance=1):
    row_count, col_count = df.shape
    mask = df.applymap(lambda x: str(x).strip() != "")  # True = non-empty

    tables = []
    visited = np.zeros(mask.shape, dtype=bool)

    def dfs(r, c, coords):
        stack = [(r, c)]
        while stack:
            rr, cc = stack.pop()
            if 0 <= rr < row_count and 0 <= cc < col_count and not visited[rr, cc]:
                visited[rr, cc] = True
                coords.append((rr, cc))
                # Explore neighbors within gap tolerance
                for dr in range(-gap_tolerance, gap_tolerance + 1):
                    for dc in range(-gap_tolerance, gap_tolerance + 1):
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < row_count and 0 <= nc < col_count and not visited[nr, nc]:
                            if mask.iat[nr, nc] or (abs(dr) <= gap_tolerance and abs(dc) <= gap_tolerance):
                                stack.append((nr, nc))

    # Step 1: Find connected blocks
    for r in range(row_count):
        for c in range(col_count):
            if mask.iat[r, c] and not visited[r, c]:
                coords = []
                dfs(r, c, coords)
                if len(coords) >= min_block_size:
                    rows = [p[0] for p in coords]
                    cols = [p[1] for p in coords]
                    rmin, rmax = min(rows), max(rows)
                    cmin, cmax = min(cols), max(cols)
                    block_df = df.iloc[rmin:rmax + 1, cmin:cmax + 1]
                    tables.append((rmin, rmax, cmin, cmax, block_df))

    results = []

    # Step 2: Run header detection
    for (rmin, rmax, cmin, cmax, block_df) in tables:
        non_empty_rows = [i for i in range(block_df.shape[0]) if block_df.iloc[i].notna().any()]
        if not non_empty_rows:
            continue

        def score_row(row_idx):
            values = [str(v).strip() for v in block_df.iloc[row_idx].tolist()]
            non_empty = sum(1 for v in values if v)
            text_like = sum(1 for v in values if v.isalpha())
            num_like = sum(1 for v in values if v.replace(".", "", 1).isdigit())
            return non_empty + text_like - num_like

        candidates = non_empty_rows[:max_header_search]
        scores = {r: score_row(r) for r in candidates}
        header_row_idx = max(scores, key=scores.get)

        # Multi-row headers
        header_rows = [list(block_df.iloc[header_row_idx].tolist())]
        for i in range(1, max_header_rows):
            if header_row_idx + i < block_df.shape[0]:
                next_score = score_row(header_row_idx + i)
                if next_score >= scores[header_row_idx] * 0.6:
                    header_rows.append(list(block_df.iloc[header_row_idx + i].tolist()))
                else:
                    break

        # Pre-header
        pre_header_context = [
            list(block_df.iloc[r].tolist())
            for r in non_empty_rows if r < header_row_idx
        ]

        # Sample rows after headers (basic)
        last_header_row = header_row_idx + len(header_rows) - 1
        sample_rows = [
            list(block_df.iloc[r].tolist())
            for r in non_empty_rows if r > last_header_row
        ][:sample_limit]

        results.append({
            "header_rows": header_rows,
            "sample_rows": sample_rows,
            "pre_header_context": pre_header_context,
            "raw_table": block_df.values.tolist(),
            "bounding_box": {
                "row_min": rmin, "row_max": rmax,
                "col_min": cmin, "col_max": cmax
            },
            "row_count": block_df.shape[0],
            "col_count": block_df.shape[1],
        })

    return results


# ------------------------------------------------
# 🔹 Utility: Representative Rows (first, mid, last)
# ------------------------------------------------
def get_representative_rows(raw_table, count=2):
    """Extract first N, middle N, and last N rows from raw_table."""
    if not raw_table:
        return []

    total_rows = len(raw_table)
    reps = []

    # First N rows
    reps.extend(raw_table[:count])

    # Middle N rows
    if total_rows > 2 * count:
        mid_start = total_rows // 2 - count // 2
        reps.extend(raw_table[mid_start:mid_start + count])

    # Last N rows
    if total_rows > count:
        reps.extend(raw_table[-count:])

    return reps


# -------------------------------
# 🔹 Main Extraction Task
# -------------------------------
def task_extract_workbook(uploaded_file_id):
    uploaded = UploadedFile.objects.get(file_id=uploaded_file_id)
    file_obj = uploaded.s3_path

    # Step 1: Load with pandas
    try:
        xls = pd.ExcelFile(file_obj)
    except Exception as e:
        AuditLog.objects.create(sheet_unit=None, action="extract_error", details={"error": str(e)})
        raise

    # Step 2: Load with openpyxl for charts/images
    try:
        wb = load_workbook(file_obj)
    except Exception as e:
        wb = None
        AuditLog.objects.create(sheet_unit=None, action="openpyxl_error", details={"error": str(e)})

    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name, header=None, dtype=str).fillna("")

        detected_tables = detect_tables_2d(df)

        for idx, table in enumerate(detected_tables, start=1):
            row_count, col_count = table["row_count"], table["col_count"]

            # Save raw_table or CSV pointer
            if row_count <= MAX_INLINE_ROWS:
                raw_table = table["raw_table"]
            else:
                tmp_csv = io.StringIO()
                pd.DataFrame(table["raw_table"]).to_csv(tmp_csv, index=False, header=False)
                csv_bytes = tmp_csv.getvalue().encode()
                object_name = f"uploaded_raw_tables/{uploaded.file_id}/{uuid.uuid4()}.csv"
                default_storage.save(object_name, io.BytesIO(csv_bytes))
                raw_table = {"csv_pointer": object_name}

            # Metadata: charts + OCR
            charts_info, ocr_results = {}, {}
            if wb:
                ws = wb[sheet_name]
                charts_info[sheet_name] = len(getattr(ws, "_charts", []))
                extracted_texts = []
                for img in getattr(ws, "_images", []):
                    try:
                        img_bytes = img._data()
                        image = Image.open(io.BytesIO(img_bytes))
                        with tempfile.TemporaryDirectory() as tmp_dir:
                            pdf_path = os.path.join(tmp_dir, "img.pdf")
                            ocr_pdf_path = os.path.join(tmp_dir, "img_ocr.pdf")
                            image.convert("RGB").save(pdf_path)

                            subprocess.run(
                                ["ocrmypdf", "--force-ocr", pdf_path, ocr_pdf_path],
                                check=True, capture_output=True
                            )

                            doc = fitz.open(ocr_pdf_path)
                            ocr_text = "\n".join([page.get_text().strip() for page in doc])
                            doc.close()

                            if ocr_text.strip():
                                extracted_texts.append(ocr_text.strip())
                    except Exception as e:
                        extracted_texts.append(f"[OCR Error: {str(e)}]")

                if extracted_texts:
                    ocr_results[sheet_name] = extracted_texts

            metadata = {
                "charts": charts_info,
                "ocr_from_images": ocr_results,
                "pre_header_context": table["pre_header_context"],
                "table_count": len(detected_tables)
            }

            # Save to DB
            sheet_unit = SheetUnit.objects.create(
                uploaded_file=uploaded,
                sheet_name=sheet_name,
                row_count=row_count,
                col_count=col_count,
                header_rows=table["header_rows"],
                sample_rows=table["sample_rows"],
                raw_table=raw_table,
                bounding_box=table["bounding_box"],
                table_index=idx,
                metadata=metadata
            )
            AuditLog.objects.create(
                sheet_unit=sheet_unit,
                action="sheet_extracted",
                details={
                    "rows": row_count,
                    "cols": col_count,
                    "charts": charts_info.get(sheet_name, 0),
                    "header_detected": table["header_rows"][:2],
                    "pre_header_count": len(table["pre_header_context"]),
                    "table_index": idx,
                    "table_count": len(detected_tables)
                }
            )

            # Representative rows for classification
            representative_rows = get_representative_rows(table["raw_table"], count=2)

            print(f"headers_row : {table['header_rows']}")
            print(f"sample_rows : {table['sample_rows']}")
            print(f"raw_table : {table['raw_table']}")
            print(f"pre_header_context : {table['pre_header_context']}")
            print(f"bounding_box : {table['bounding_box']}")
            print(f"representative rows: {representative_rows}")
            # Run classification
            # rule_based_classify(
            #     header_rows=table["header_rows"],
            #     sample_rows=table["sample_rows"],
            #     pre_header_context=table["pre_header_context"],
            #     bounding_box=table["bounding_box"],
            #     representative_rows=representative_rows
            # )

    return ""

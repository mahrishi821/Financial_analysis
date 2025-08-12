# import os
# import zipfile
# from .text_extractors import extract_text_from_file
# from documents.models import ExtractedDocument
#
# def extract_zip_and_save(zip_file_path, output_dir, upload_instance):
#     os.makedirs(output_dir, exist_ok=True)
#
#     with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
#         zip_ref.extractall(output_dir)
#         for file_name in zip_ref.namelist():
#             full_path = os.path.join(output_dir, file_name)
#             if os.path.isfile(full_path):
#                 preview = extract_text_from_file(full_path)
#                 ExtractedDocument.objects.create(
#                     upload=upload_instance,
#                     file_name=file_name,
#                     file_path=full_path,
#                     preview_text=preview[:2000]  # truncate preview if needed
#                 )

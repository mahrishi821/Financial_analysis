# import os
# import textract
#
# def extract_text_from_file(file_path):
#     try:
#         if file_path.endswith(('.pdf', '.docx', '.pptx', '.txt', '.xlsx')):
#             return textract.process(file_path).decode('utf-8')
#     except Exception as e:
#         print(f"Could not extract {file_path}: {e}")
#     return ""

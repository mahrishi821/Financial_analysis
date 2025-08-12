# import os
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import DocumentUpload
# from django.conf import settings
# from .utils.zip_handler import extract_zip_and_save
#
# @receiver(post_save, sender=DocumentUpload)
# def extract_uploaded_zip(sender, instance, created, **kwargs):
#     if not created:
#         return
#
#     output_dir = os.path.join(
#         settings.MEDIA_ROOT,
#         'extracted',
#         str(instance.company.id),
#         instance.upload_date.strftime('%Y_%m_%d')
#     )
#
#     try:
#         extract_zip_and_save(instance.zip_file.path, output_dir, instance)
#     except Exception as e:
#         print(f"Error extracting ZIP: {e}")
#

from rest_framework import viewsets, status
from rest_framework.decorators import action
from common.jsonResponse.response import JSONResponseSender
from common.third_party_integration.pdf_paraphraser import Paraphrasepdf
from common.third_party_integration.doc_paraphraser import DocumentParaphraser
from common.third_party_integration.excel_pharaphraser import ExcelDataProcessor
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from common.models import DocumentUpload, ExtractedDocument,Company
from common.serializers import DocumentUploadSerializer




class DocumentUploadViewSet(viewsets.ModelViewSet):

    queryset = DocumentUpload.objects.all().order_by('-upload_date')
    serializer_class = DocumentUploadSerializer

    @action(detail=False, methods=['get'])
    def by_company(self, request):
        company_id = request.query_params.get('company')
        if not company_id:
            return Response({"error": "Missing 'company' query param"}, status=400)
        uploads = self.queryset.filter(company_id=company_id).order_by('-upload_date')
        serializer = self.get_serializer(uploads, many=True)
        return Response(serializer.data)



class ParaphrasePDFView(APIView):
    parser_class = [MultiPartParser]

    def post(self, request, format=None):
        uploaded_file = request.FILES.get('file')
        print(f"uploaded_file type: {type(uploaded_file)}")
        if not uploaded_file or not uploaded_file.name.endswith('.pdf'):
            return JSONResponseSender.send_error('400','Only PDF files are supported.','Only PDF files are supported.')

        try:
            file_bytes = uploaded_file.read()
            pdf_tool = Paraphrasepdf()

            # Extract and paraphrase
            original_text = pdf_tool.extract_text_from_pdf(file_bytes)


            if not original_text:
                return JSONResponseSender.send_error('400','No text found in PDF file','No text found in PDF file')

            # paraphrased_text = pdf_tool.paraphrase_text(original_text)

            # return JSONResponseSender.send_success(paraphrased_text)
            return JSONResponseSender.send_success(original_text)
        except Exception as e:
            return JSONResponseSender.send_error('400','Error parsing PDF file',str(e))


class ParaphraseDOCXView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        uploaded_file = request.FILES.get('file')

        if not uploaded_file or not uploaded_file.name.endswith('.docx'):
            return JSONResponseSender.send_error('400', 'Only DOCX files are supported.', 'Only DOCX files are supported.')

        try:
            file_bytes = uploaded_file.file  # Access the file-like object
            doc_tool = DocumentParaphraser()

            # Extract and paraphrase
            original_text = doc_tool.extract_text_from_docx(file_bytes)

            if not original_text.strip():
                return JSONResponseSender.send_error('400', 'No text found in DOCX file.', 'No text found in DOCX file.')

            # paraphrased_text = doc_tool.paraphrase_text(original_text)

            return JSONResponseSender.send_success(original_text)
            # return JSONResponseSender.send_success(paraphrased_text)

        except Exception as e:
            return JSONResponseSender.send_error('500', 'Error processing DOCX file.', str(e))

class ParaphraseExcelView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file or not uploaded_file.name.endswith(".xlsx"):
            return JSONResponseSender.send_error(
                '400', 'Only XLSX files are supported.', 'Only XLSX files are supported.'
            )

        try:
            file_bytes = uploaded_file.file
            excel_tool = ExcelDataProcessor()

            # Load and clean
            df = excel_tool.load_excel(file_bytes)
            print(f"df : {df}")
            # cleaned_df = excel_tool.clean_data(df)

            # Optional: Paraphrase a specific column (e.g., 'description')
            # if 'description' in cleaned_df.columns:
            #     paraphrased_df = excel_tool.paraphrase_column(cleaned_df, 'description')
            # else:
            #     paraphrased_df = cleaned_df

            # Convert DataFrame to JSON serializable format
            # data = paraphrased_df.to_dict(orient="records")
            # data = cleaned_df.to_dict(orient="records")

            return JSONResponseSender.send_success(file_bytes)

        except Exception as e:
            return JSONResponseSender.send_error('500', 'Error processing Excel file.', str(e))


class DocumentUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            uploaded_file = request.FILES.get('file')
            print(f"uploaded_file type: {type(uploaded_file)}")
            company_id = request.data.get('company')
            print(f"company_id: {company_id}")
            if not uploaded_file or not uploaded_file.name.endswith('.zip'):
                return Response({'error': 'Only ZIP files are supported.'}, status=status.HTTP_400_BAD_REQUEST)

            if not company_id:
                return Response({'error': 'Company ID is required.'}, status=status.HTTP_400_BAD_REQUEST)



            company = Company.objects.get(id=company_id)
            print(f"company: {company}")
            # Save DocumentUpload record
            doc_upload = DocumentUpload.objects.create(
                company=company,
                zip_file=uploaded_file,
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous',
                file_size=uploaded_file.size
            )

            # Extract files
            # extracted_files = []
            # extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted', str(doc_upload.id))
            # os.makedirs(extract_path, exist_ok=True)
            #
            # zip_temp_path = doc_upload.zip_file.path
            # with zipfile.ZipFile(zip_temp_path, 'r') as zip_ref:
            #     zip_ref.extractall(extract_path)
            #     for filename in zip_ref.namelist():
            #         extracted_file_path = os.path.join(extract_path, filename)
            #
            #         # Save ExtractedDocument model (if defined)
            #         if os.path.isfile(extracted_file_path):
            #             with open(extracted_file_path, 'rb') as f:
            #                 content = ContentFile(f.read(), name=filename)
            #
            #                 ExtractedDocument.objects.create(
            #                     document_upload=doc_upload,
            #                     filename=filename,
            #                     file=content
            #                 )
            #
            # # Serialize with nested extracted files
            # serializer = DocumentUploadSerializer(doc_upload)
            # return JSONResponseSender.send_success(serializer.data)
            return JSONResponseSender.send_success("uploaded successfully")
        except Company.DoesNotExist:
            return JSONResponseSender.send_error('500', 'Error processing zip file.',)

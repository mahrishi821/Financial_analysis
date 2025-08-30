from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from common.jsonResponse.response import JSONResponseSender
from common.models import ChatbotUpload, ChatbotChunk, ChatbotSession
from common.serializers import ChatbotUploadSerializer, ChatbotSessionSerializer
from .utils.file_text_extractor import FileTextExtractor
from .utils.pinecone_store import PineconeStore
from .utils.llm import OpenRouterLLM
import os

# Initialize shared utilities (singleton style)
extractor = FileTextExtractor()
vector_store = PineconeStore()
llm = OpenRouterLLM()


class ChatbotUploadView(APIView):
    """
    Endpoint to upload document for chatbot usage.
    """
    def post(self, request):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return JSONResponseSender.send_error("400", "No file provided", "No file provided")

        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in [".pdf", ".xls", ".xlsx", ".doc", ".docx"]:
            return JSONResponseSender.send_error("400", "Unsupported file type", "support only excel, docs and pdf")
        try:
            upload = ChatbotUpload.objects.create(
                uploaded_by=request.user,
                file=uploaded_file,
                file_name=uploaded_file.name,
                file_type=uploaded_file.name.split(".")[-1]
            )

            return JSONResponseSender.send_success( {
                "message": "File uploaded successfully",
                "upload_id": upload.id,
                "uploaded_by": upload.uploaded_by.name,
            })
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))


class ProcessChatbotUploadView(APIView):
    """
    Process uploaded file: extract text, chunk, index into Pinecone.
    """
    def post(self, request, pk):

        # Extract text
        try:
            upload = get_object_or_404(ChatbotUpload, id=pk, uploaded_by=request.user)
            text, file_type = extractor.extract(upload.file.path, upload.file.read())

            if not text:
                return JSONResponseSender.send_error("400", "Unsupported or empty file","Unsupported or empty file")

            # Chunk & store in Pinecone
            chunk_size = 300
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            vector_ids = vector_store.add_chunks(upload.id, chunks)

            # Save chunk metadata in DB
            for vid, chunk in zip(vector_ids, chunks):
                ChatbotChunk.objects.create(upload=upload, chunk_text=chunk, vector_id=vid)

            upload.processed = True
            upload.save()

            return JSONResponseSender.send_success({"message": "File processed & indexed"})
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))

class ChatbotQueryView(APIView):
    """
    Query chatbot: retrieve chunks from Pinecone and generate answer using OpenRouter LLM.
    """
    def post(self, request, pk):
        upload = get_object_or_404(ChatbotUpload, id=pk, uploaded_by=request.user)
        question = request.data.get("question")

        try:
            if not question:
                return JSONResponseSender.send_error("error", "Question is required","Question is required")

            # Retrieve top chunks
            top_chunks = vector_store.query(upload.id, question, top_k=3)
            context = "\n".join(top_chunks)

            # Generate answer
            answer = llm.generate_answer(question, context)

            # Save session
            session = ChatbotSession.objects.create(
                # user=request.user,
                upload=upload,
                question=question,
                answer=answer
            )

            return JSONResponseSender.send_success({
                "answer": answer,
                "session_id": session.id
            })
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))


class ChatbotHistoryView(APIView):
    """
    Retrieve chat history for a given upload.
    """
    def get(self, request, pk):
        try:
            upload = get_object_or_404(ChatbotUpload, id=pk, uploaded_by=request.user)
            sessions = ChatbotSession.objects.filter(upload=upload).order_by("-created_at")
            return JSONResponseSender.send_success(ChatbotSessionSerializer(sessions, many=True).data)
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))


class ChatbotUserSessionView(APIView):
    """
    Retrieve number of chat session for given user
    """
    def get(self, request):
        try:
            sessions_count= ChatbotSession.objects.filter(upload__uploaded_by=request.user).count()
            return JSONResponseSender.send_success({"sessions_count": sessions_count})
        except Exception as e:
            return JSONResponseSender.send_error("500", str(e), str(e))
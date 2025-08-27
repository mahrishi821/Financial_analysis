import os
import uuid
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer


class PineconeStore:
    def __init__(self):
        # Load Pinecone credentials from env
        self.api_key = os.environ.get("PINECONE_API_KEY")
        self.index_name = os.environ.get("PINECONE_INDEX_NAME", "chatbot")

        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables.")

        # ✅ New Pinecone client
        self.pc = Pinecone(api_key=self.api_key)

        # Check if index exists, else create it
        existing_indexes = self.pc.list_indexes().names()
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=384,          # for all-MiniLM-L6-v2 embeddings
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"   # update if your account is in another region
                )
            )

        # Connect to index
        self.index = self.pc.Index(self.index_name)

        # Load embedding model once
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def add_chunks(self, upload_id, chunks):
        """
        Store chunks in Pinecone under a namespace (upload_id).
        Returns list of vector IDs.
        """
        embeddings = self.embedder.encode(chunks).tolist()

        vectors, vector_ids = [], []
        for chunk, embedding in zip(chunks, embeddings):
            vid = str(uuid.uuid4())
            vectors.append({
                "id": vid,
                "values": embedding,
                "metadata": {"text": chunk, "upload_id": str(upload_id)}
            })
            vector_ids.append(vid)

        self.index.upsert(vectors=vectors, namespace=str(upload_id))
        return vector_ids

    def query(self, upload_id, question, top_k=3):
        """
        Query Pinecone for top chunks related to a question.
        Returns list of matched texts.
        """
        q_emb = self.embedder.encode([question]).tolist()[0]
        results = self.index.query(
            vector=q_emb,
            namespace=str(upload_id),
            top_k=top_k,
            include_metadata=True
        )
        return [match["metadata"]["text"] for match in results["matches"]]

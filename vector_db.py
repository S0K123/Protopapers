import chromadb


class VectorStoreManager:

    def __init__(self, collection_name: str = "pdf_rag"):
        self.chroma_client = chromadb.Client()
        self.collection_name = collection_name
        
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
        except Exception:
            pass

        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

    def add_chunks(self, chunks: list[str]):
        """Indexes chunks instantly into ChromaDB using local vector embeddings."""
        if not chunks:
            return

        documents = chunks
        ids = [f"chunk_{idx}" for idx in range(len(chunks))]

        self.collection.add(
            ids=ids,
            documents=documents
        )

    def search_similar(self, query: str, top_k: int = 8) -> str:
        """Queries the local collection and fetches relevant text context."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        retrieved_docs = results["documents"][0]
        return "\n\n--- RETRIEVED CONTEXT ---\n\n".join(retrieved_docs)
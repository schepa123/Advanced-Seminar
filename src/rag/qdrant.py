from qdrant_client.http.models import Distance, VectorParams
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings


class QdrantConnection():
    def __init__(
        self,
        embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
            model="text-embedding-3-large"
        ),
        port: int = 6333,
        local: bool = True
    ) -> None:
        self.port = port
        self.local = local
        self.client = self.init_client()
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name="collection",
            embedding=embeddings,
        )

    def init_client(self) -> QdrantClient:
        """
        Inits the client with an empty collection.

        Args:
            None.

        Returns:
            QdrantClient: The initialized Client.
        """
        if self.local:
            client = QdrantClient(f"http://localhost:{self.port}")
        else:
            client = QdrantClient(":memory:")

        try:
            client.create_collection(
                collection_name="collection",
                vectors_config=VectorParams(
                    size=3072,
                    distance=Distance.COSINE
                ),
            )
        except Exception:  # Collection already exists
            pass

        return client

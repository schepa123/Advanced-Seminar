import os
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from uuid import uuid4
from agents_src.agent_data_definitions import MetaExpertState
from .qdrant import QdrantConnection # ÄNDERE DAS AUF WAS ALLGEMEINERS
from langchain_core.documents import Document
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker



class IMDbReviewVectorStoreLoader():
    def __init__(
        self,
        path: str,
        vector_store: QdrantConnection,
        chunking_strategy: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        add_start_index: bool = True
    ) -> None:
        self.vector_store = vector_store
        self.path = path
        self.file_data = self.load_files()
        self.movies_with_uuid = self.define_movies()
        self.text_splitter = self.select_text_splitter(
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=add_start_index
        )
        self.add_uuid_to_df()

    def select_text_splitter(
        self,
        chunking_strategy: str,
        chunk_size: int,
        chunk_overlap: int,
        add_start_index: bool
    ) -> RecursiveCharacterTextSplitter | SemanticChunker:
        """
        Selects the chunking strategy.

        Args:
            chunking_strategy(str): Name of strategy

        Returns:
            RecursiveCharacterTextSplitter | SemanticChunker: LangChain
        """
        match chunking_strategy:
            case "RecursiveCharacterTextSplitter":
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    add_start_index=add_start_index,
                )
            case "SemanticChunker":
                text_splitter = SemanticChunker(OpenAIEmbeddings())

        return text_splitter

    def load_files(self) -> dict[str, pd.DataFrame]:
        """
        Loads the files of the IMDb dataset.

        Args:
            None.

        Returns:
            dict[str, str]: Dict with file name as key and
            corresponding dataframe as values.
        """
        files_read = {}
        files = [
            f for f in os.listdir(self.path)
            if os.path.isfile(os.path.join(self.path, f))
        ]
        for file in files:
            files_read[file] = pd.read_json(os.path.join(
                self.path,
                file
            ))[["movie", "review_detail"]]
        return files_read

    def define_movies(self) -> dict[str, str]:
        """
        Extractes the movies from the data and assigns UUID for each.

        Args:
            None.

        Returns:
            dict[str, str]: Movie name as key and uuid as value.
        """
        all_movies = []
        for _, df in self.file_data.items():
            all_movies.extend(df["movie"].to_list())
            all_movies = list(set(all_movies))

        return {movie: str(uuid4())for movie in all_movies}

    def add_uuid_to_df(self) -> None:
        """
        Adds UUID to each dataframe of the class.

        Args:
            None.

        Returns:
            None.
        """
        for _, df in self.file_data.items():
            df['movie_uuid'] = df['movie'].map(self.movies_with_uuid)

    def load_to_vector_store(self) -> None:
        """
        Creates Documents out of dataframe and loads them into
        the vector store.

        Args:
            None.

        Returns:
            None.
        """
        for _, df in self.file_data.items():
            # REMOVE; THIS IS JUST FOR TESTING
            # df = df.sample(23)
            # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
            documents = []
            for row in df.itertuples(index=False):
                documents.append(
                    Document(
                        page_content=row.review_detail,
                        metadata={
                            "movie": row.movie,
                            "movie_uuid": row.movie_uuid
                        }
                    )
                )

            chunks = self.text_splitter.split_documents(documents)
            self.vector_store.vector_store.add_documents(chunks)

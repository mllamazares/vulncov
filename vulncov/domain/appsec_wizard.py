import logging
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain.text_splitter import Language
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class AppSecWizard:
    def __init__(self, repo_path, ollama_url, ollama_model="codellama:latest"):
        """
        Initializes the AppSecWizard class.

        Args:
            repo_path (str): Path to the repository with source code.
            ollama_url (str): The URL for the Ollama LLM server.
        """
        self.repo_path = repo_path
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model

        self.documents = self._load_documents()
        self.embeddings = self._generate_embeddings()
        self.texts = self._split_documents()
        self.db = self._create_vector_store()

    def _load_documents(self):
        """
        Loads the source code documents from the specified repository path.

        Returns:
            list: A list of loaded documents from the repository.
        """
        logging.info(f"👀 Loading source code from {self.repo_path}...")
        loader = GenericLoader.from_filesystem(
            self.repo_path,
            glob="**/*",
            suffixes=[".py"],
            parser=LanguageParser(language=Language.PYTHON),
        )
        documents = loader.load()
        logging.info(f"Loaded {len(documents)} files from the repository.")
        return documents

    def _generate_embeddings(self):
        """
        Generates embeddings using the HuggingFace model.

        Returns:
            HuggingFaceEmbeddings: The embeddings model.
        """
        logging.info("🤗 Generating embeddings using HuggingFace.")
        embeddings = HuggingFaceEmbeddings()
        return embeddings

    def _split_documents(self):
        """
        Splits the loaded documents into chunks for vector store indexing.

        Returns:
            list: A list of text chunks for indexing.
        """
        logging.info("✂️ Splitting documents into chunks for FAISS vector store.")
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=8000,
            chunk_overlap=20
        )
        texts = splitter.split_documents(self.documents)
        logging.info(f"Split documents into {len(texts)} chunks for indexing.")
        return texts

    def _create_vector_store(self):
        """
        Creates a FAISS vector store from the document embeddings.

        Returns:
            FAISS: The FAISS vector store object.
        """
        logging.info("📚 Creating FAISS vector store.")
        db = FAISS.from_documents(self.texts, self.embeddings)
        return db

    def get_retriever(self):
        """
        Returns a retriever from the FAISS vector store for document search.

        Returns:
            Retriever: The FAISS retriever for document searches.
        """
        return self.db.as_retriever(search_type="mmr", search_kwargs={"k": 8})

    def create_chain(self, template):
        """
        Creates a LangChain processing chain for interacting with the LLM.

        Args:
            template (str): The prompt template for LLM interaction.

        Returns:
            Chain: A chain of processors for LLM queries.
        """
        prompt = PromptTemplate.from_template(template)
        retriever = self.get_retriever()
        llm = OllamaLLM(model=self.ollama_model, temperature=0.6, base_url=self.ollama_url)

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        return chain

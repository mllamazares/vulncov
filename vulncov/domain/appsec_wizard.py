import logging
from langchain_ollama import OllamaLLM
from langchain_openai import OpenAI
from langchain_anthropic import AnthropicLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class AppSecWizard:
    def __init__(self, service, api_key=None, base_url=None):
        """
        Initialize the LLMProvider class with various LLM service options.
        
        Args:
            service (str): The LLM service to use (e.g., 'ollama', 'openai', 'anthropic').
            api_key (str): The API key for external LLM services.
            model (str): The model name (defaults to "codellama:latest" for Ollama).
            base_url (str): Base URL for self-hosted models like Ollama.
        """
        self.service = service
        self.api_key = api_key
        self.base_url = base_url

    def get_llm(self):
        """
        Return the LLM based on the selected service.
        """
        if self.service == 'ollama':
            return OllamaLLM(base_url=self.base_url)
        elif self.service == 'openai':
            return OpenAI(api_key=self.api_key)
        elif self.service == 'anthropic':
            return Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported LLM service: {self.service}")

    def create_chain(self, template, retriever):
        """
        Creates a LangChain processing chain for interacting with the LLM.
        
        Args:
            template (str): The prompt template for LLM interaction.
            retriever: The FAISS vector store retriever.

        Returns:
            Chain: A chain of processors for LLM queries.
        """
        prompt = PromptTemplate.from_template(template)
        llm = self.get_llm()

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain

"""
RAG Service for SAP Knowledge Base using Pinecone and LangChain
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple

# Try to import RAG dependencies, handle gracefully if not available
try:
    from langchain_pinecone import PineconeVectorStore
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain_core.prompts import ChatPromptTemplate
    from pinecone import Pinecone, ServerlessSpec
    RAG_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"RAG dependencies not available: {e}")
    RAG_DEPENDENCIES_AVAILABLE = False

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for SAP knowledge base using Pinecone and OpenAI"""
    
    # Configuration constants
    INDEX_NAME = 'sap-onboarding-faq'
    EMBEDDING_MODEL = 'text-embedding-3-large'
    LLM_MODEL = 'gpt-4'
    LLM_TEMPERATURE = 0.3
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 0
    DEFAULT_K = 3
    DEFAULT_SCORE_THRESHOLD = 0.7
    
    def __init__(self):
        """Initialize RAG service with Pinecone and OpenAI"""
        self.initialized = False
        self.pc = None
        self.index = None
        self.embeddings = None
        self.llm = None
        self.vectorstore = None
        
        if not self._check_dependencies():
            return
            
        if not self._load_api_keys():
            return
            
        try:
            self._initialize_components()
            self.initialized = True
            logger.info("RAG service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            self.initialized = False
    
    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        if not RAG_DEPENDENCIES_AVAILABLE:
            logger.warning("RAG dependencies not available - service disabled")
            return False
        return True
    
    def _load_api_keys(self) -> bool:
        """Load and validate API keys"""
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.pinecone_api_key or not self.openai_api_key:
            logger.warning("Missing API keys for RAG service")
            return False
        return True
    
    def _initialize_components(self):
        """Initialize all RAG components"""
        self._initialize_pinecone()
        self._initialize_embeddings()
        self._initialize_llm()
        self._initialize_vectorstore()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and create index if needed"""
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Create index if it doesn't exist
        if self.INDEX_NAME not in self.pc.list_indexes().names():
            logger.info(f"Creating Pinecone index: {self.INDEX_NAME}")
            self.pc.create_index(
                name=self.INDEX_NAME,
                dimension=3072,  # OpenAI text-embedding-3-large dimension
                metric='euclidean',
                deletion_protection='enabled',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        
        self.index = self.pc.Index(self.INDEX_NAME)
        logger.info(f"Connected to Pinecone index: {self.INDEX_NAME}")
    
    def _initialize_embeddings(self):
        """Initialize OpenAI embeddings"""
        self.embeddings = OpenAIEmbeddings(
            model=self.EMBEDDING_MODEL,
            openai_api_key=self.openai_api_key
        )
        logger.info(f"OpenAI embeddings initialized with model: {self.EMBEDDING_MODEL}")
    
    def _initialize_llm(self):
        """Initialize ChatOpenAI for generation"""
        self.llm = ChatOpenAI(
            model=self.LLM_MODEL,
            temperature=self.LLM_TEMPERATURE,
            openai_api_key=self.openai_api_key
        )
        logger.info(f"ChatOpenAI initialized with model: {self.LLM_MODEL}")
    
    def _initialize_vectorstore(self):
        """Initialize Pinecone vector store"""
        self.vectorstore = PineconeVectorStore(
            index=self.index,
            embedding=self.embeddings
        )
        logger.info("Pinecone vector store initialized")
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store"""
        if not self.initialized:
            logger.error("RAG service not initialized")
            return False
        
        if not documents:
            logger.warning("No documents provided to add")
            return False
        
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.CHUNK_SIZE,
                chunk_overlap=self.CHUNK_OVERLAP
            )
            split_docs = text_splitter.split_documents(documents)
            self.vectorstore.add_documents(split_docs)
            logger.info(f"Successfully added {len(split_docs)} document chunks to vector store")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    def query(self, question: str, k: int = DEFAULT_K, score_threshold: float = DEFAULT_SCORE_THRESHOLD) -> Dict[str, Any]:
        """Query the knowledge base and generate a response"""
        if not self.initialized:
            return self._create_error_response("RAG service not initialized")
        
        if not question or not question.strip():
            return self._create_error_response("Empty question provided")
        
        try:
            logger.info(f"Processing query: '{question[:50]}...' with k={k}, threshold={score_threshold}")
            
            # Retrieve and filter documents
            docs, scores = self._retrieve_documents(question, k, score_threshold)
            
            if not docs:
                return self._create_no_results_response(score_threshold)
            
            # Generate response
            context = self._create_context(docs)
            response = self._generate_response(context, question)
            sources = self._extract_sources(docs)
            
            logger.info(f"Successfully generated response using {len(docs)} documents")
            
            return {
                "response": response,
                "sources": sources,
                "context_docs": len(docs),
                "question": question,
                "scores": scores,
                "score_threshold": score_threshold
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return self._create_error_response(f"Query processing failed: {str(e)}")
    
    def _retrieve_documents(self, question: str, k: int, score_threshold: float) -> Tuple[List[Document], List[float]]:
        """Retrieve and filter documents based on similarity scores"""
        # Retrieve more documents than needed to allow for filtering
        docs_with_scores = self.vectorstore.similarity_search_with_score(question, k=k*2)
        
        # Filter documents by score threshold (lower scores are better for cosine similarity)
        filtered_docs = [(doc, score) for doc, score in docs_with_scores if score <= score_threshold]
        
        # Take only the top k documents that meet the threshold
        docs = [doc for doc, score in filtered_docs[:k]]
        scores = [score for doc, score in filtered_docs[:k]]
        
        return docs, scores
    
    def _create_context(self, docs: List[Document]) -> str:
        """Create context string from retrieved documents"""
        return "\n\n".join([doc.page_content for doc in docs])
    
    def _extract_sources(self, docs: List[Document]) -> List[str]:
        """Extract source information from documents"""
        return [doc.metadata.get('source', 'Unknown') for doc in docs]
    
    def _generate_response(self, context: str, question: str) -> str:
        """Generate response using RAG chain"""
        prompt = ChatPromptTemplate.from_template("""
You are a helpful SAP assistant. Answer the user's question using ONLY the provided context.

Context: {context}
Question: {question}

Instructions:
- Answer ONLY using information from the context above
- Do NOT add any information not in the context
- If the context doesn't have enough information, say "I don't have enough information in my knowledge base"
- Keep your answer concise (1-2 sentences)
- Use the exact information from the context

Answer:
""")
        
        rag_chain = (
            {"context": lambda x: context, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        response = rag_chain.invoke(question)
        return self._format_response(response)
    
    def _format_response(self, response: str) -> str:
        """Format response for better readability with proper spacing"""
        if not response:
            return response
            
        # Split response into sentences
        sentences = response.split('. ')
        
        # Add line breaks between sentences for better readability
        formatted_response = '.\n\n'.join(sentences)
        
        # Clean up any double line breaks
        formatted_response = formatted_response.replace('\n\n\n', '\n\n')
        
        # Ensure it ends with a period
        if not formatted_response.endswith('.'):
            formatted_response += '.'
            
        return formatted_response
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "response": "I'm here to help with SAP questions, but my knowledge base is currently unavailable. Please contact IT support for assistance.",
            "sources": [],
            "error": error_message
        }
    
    def _create_no_results_response(self, score_threshold: float) -> Dict[str, Any]:
        """Create response when no relevant documents are found"""
        return {
            "response": "I couldn't find specific information about your question in the knowledge base. Please contact SAP support for assistance.",
            "sources": [],
            "error": f"No relevant documents found above score threshold {score_threshold}",
            "context_docs": 0
        }
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        if not self.initialized:
            return {"error": "RAG service not initialized"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "metric": stats.metric,
                "namespaces": stats.namespaces,
                "index_name": self.INDEX_NAME
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"error": str(e)}
    
    def is_healthy(self) -> bool:
        """Check if the RAG service is healthy and ready to use"""
        return self.initialized and all([
            self.pc is not None,
            self.index is not None,
            self.embeddings is not None,
            self.llm is not None,
            self.vectorstore is not None
        ])


# Global RAG service instance
rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service
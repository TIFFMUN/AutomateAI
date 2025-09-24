"""
Pinecone Index Management Script
Handles truncating and populating Pinecone index with Q&A data
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import RAG dependencies
try:
    from langchain_pinecone import PineconeVectorStore
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    from pinecone import Pinecone, ServerlessSpec
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logging.error(f"Required dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PineconeManager:
    """Manages Pinecone index operations including truncation and population"""
    
    # Configuration constants (matching RAGService)
    INDEX_NAME = 'sap-onboarding-faq'
    EMBEDDING_MODEL = 'text-embedding-3-large'
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 0
    
    def __init__(self):
        """Initialize Pinecone manager"""
        self.pc = None
        self.index = None
        self.embeddings = None
        self.vectorstore = None
        
        if not self._check_dependencies():
            raise ImportError("Required dependencies not available")
        
        if not self._load_api_keys():
            raise ValueError("Missing required API keys")
        
        self._initialize_components()
    
    def _check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        return DEPENDENCIES_AVAILABLE
    
    def _load_api_keys(self) -> bool:
        """Load and validate API keys"""
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.pinecone_api_key or not self.openai_api_key:
            logger.error("Missing PINECONE_API_KEY or OPENAI_API_KEY")
            return False
        return True
    
    def _initialize_components(self):
        """Initialize Pinecone components"""
        self._initialize_pinecone()
        self._initialize_embeddings()
        self._initialize_vectorstore()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and connect to index"""
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Check if index exists
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
    
    def _initialize_vectorstore(self):
        """Initialize Pinecone vector store"""
        self.vectorstore = PineconeVectorStore(
            index=self.index,
            embedding=self.embeddings
        )
        logger.info("Pinecone vector store initialized")
    
    def truncate_index(self) -> bool:
        """Truncate all vectors from the Pinecone index"""
        try:
            logger.info("Starting index truncation...")
            
            # Get current stats
            stats = self.index.describe_index_stats()
            total_vectors = stats.total_vector_count
            logger.info(f"Current index has {total_vectors} vectors")
            
            if total_vectors == 0:
                logger.info("Index is already empty")
                return True
            
            # Delete all vectors by namespace (default namespace is "")
            self.index.delete(delete_all=True)
            
            # Wait for deletion to complete
            import time
            time.sleep(5)
            
            # Verify deletion
            new_stats = self.index.describe_index_stats()
            new_total = new_stats.total_vector_count
            
            if new_total == 0:
                logger.info("Successfully truncated index")
                return True
            else:
                logger.warning(f"Index still has {new_total} vectors after truncation")
                return False
                
        except Exception as e:
            logger.error(f"Error truncating index: {e}")
            return False
    
    def populate_with_qa_data(self, qa_data: List[Dict[str, str]]) -> bool:
        """Populate index with Q&A data"""
        try:
            logger.info(f"Starting population with {len(qa_data)} Q&A pairs...")
            
            # Convert Q&A data to documents
            documents = []
            for i, qa in enumerate(qa_data):
                # Create a combined text for better retrieval
                combined_text = f"Question: {qa['question']}\n\nAnswer: {qa['answer']}"
                
                # Add metadata for better organization
                metadata = {
                    'source': 'sap_qa_database',
                    'question_id': i + 1,
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'category': qa.get('category', 'general'),
                    'timestamp': datetime.now().isoformat()
                }
                
                document = Document(
                    page_content=combined_text,
                    metadata=metadata
                )
                documents.append(document)
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.CHUNK_SIZE,
                chunk_overlap=self.CHUNK_OVERLAP
            )
            split_docs = text_splitter.split_documents(documents)
            
            logger.info(f"Split into {len(split_docs)} document chunks")
            
            # Add to vector store
            self.vectorstore.add_documents(split_docs)
            
            logger.info("Successfully populated index with Q&A data")
            return True
            
        except Exception as e:
            logger.error(f"Error populating index: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get current index statistics"""
        try:
            stats = self.index.describe_index_stats()
            
            # Convert namespaces to a serializable format
            namespaces_dict = {}
            if stats.namespaces:
                for namespace, summary in stats.namespaces.items():
                    namespaces_dict[namespace] = {
                        "vector_count": summary.vector_count
                    }
            
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "metric": stats.metric,
                "namespaces": namespaces_dict,
                "index_name": self.INDEX_NAME
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"error": str(e)}
    
    def test_query(self, question: str) -> Dict[str, Any]:
        """Test a query against the populated index"""
        try:
            docs_with_scores = self.vectorstore.similarity_search_with_score(question, k=3)
            
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    "content": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata
                })
            
            return {
                "question": question,
                "results": results,
                "total_results": len(results)
            }
        except Exception as e:
            logger.error(f"Error testing query: {e}")
            return {"error": str(e)}


def load_qa_data_from_file(file_path: str = "data/sap_qa_database.json") -> List[Dict[str, str]]:
    """Load Q&A data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('sap_qa_database', [])
    except FileNotFoundError:
        logger.warning(f"Q&A data file not found: {file_path}")
        return load_sample_qa_data()
    except Exception as e:
        logger.error(f"Error loading Q&A data: {e}")
        return load_sample_qa_data()


def load_sample_qa_data() -> List[Dict[str, str]]:
    """Load sample Q&A data for testing (fallback)"""
    return [
        {
            "question": "What is SAP?",
            "answer": "SAP (Systems, Applications & Products in Data Processing) is a German multinational software corporation that makes enterprise software to manage business operations and customer relations.",
            "category": "general"
        },
        {
            "question": "How do I access SAP Fiori?",
            "answer": "SAP Fiori can be accessed through your web browser by navigating to the Fiori launchpad URL provided by your IT department. You'll need your SAP user credentials to log in.",
            "category": "access"
        }
    ]


def main():
    """Main function to demonstrate Pinecone management"""
    try:
        # Initialize manager
        manager = PineconeManager()
        
        # Show current stats
        print("Current index stats:")
        stats = manager.get_index_stats()
        print(json.dumps(stats, indent=2))
        
        # Ask user what they want to do
        print("\nOptions:")
        print("1. Truncate index (delete all vectors)")
        print("2. Populate with sample Q&A data")
        print("3. Truncate and populate")
        print("4. Test query")
        print("5. Show stats only")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\nTruncating index...")
            success = manager.truncate_index()
            if success:
                print("✅ Index truncated successfully")
            else:
                print("❌ Failed to truncate index")
        
        elif choice == "2":
            print("\nPopulating with Q&A data from file...")
            qa_data = load_qa_data_from_file()
            success = manager.populate_with_qa_data(qa_data)
            if success:
                print(f"✅ Index populated successfully with {len(qa_data)} Q&A pairs")
            else:
                print("❌ Failed to populate index")
        
        elif choice == "3":
            print("\nTruncating and populating...")
            truncate_success = manager.truncate_index()
            if truncate_success:
                qa_data = load_qa_data_from_file()
                populate_success = manager.populate_with_qa_data(qa_data)
                if populate_success:
                    print(f"✅ Index truncated and populated successfully with {len(qa_data)} Q&A pairs")
                else:
                    print("❌ Failed to populate index")
            else:
                print("❌ Failed to truncate index")
        
        elif choice == "4":
            question = input("\nEnter a test question: ").strip()
            if question:
                print(f"\nTesting query: '{question}'")
                results = manager.test_query(question)
                print(json.dumps(results, indent=2))
        
        elif choice == "5":
            print("\nCurrent index stats:")
            stats = manager.get_index_stats()
            print(json.dumps(stats, indent=2))
        
        else:
            print("Invalid choice")
        
        # Show final stats
        print("\nFinal index stats:")
        final_stats = manager.get_index_stats()
        print(json.dumps(final_stats, indent=2))
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

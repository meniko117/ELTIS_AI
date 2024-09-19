import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SimpleNodeParser

# Load environment variables from .env file
load_dotenv()

# Path to your document(s)
DOCUMENTS_DIR = os.getenv('DOCUMENTS_DIR')

# Path to save the index
PERSIST_DIR = os.getenv('PERSIST_DIR', "./my_test_storage")

documents = SimpleDirectoryReader(DOCUMENTS_DIR).load_data()
 
 # Create a parser with custom chunk size and overlap
parser = SimpleNodeParser.from_defaults(
     chunk_size=150,  # Adjust this value as needed
     chunk_overlap=30  # Adjust this value as needed
 )
 
# Parse the documents into nodes
nodes = parser.get_nodes_from_documents(documents)

# Create the index
index = VectorStoreIndex(nodes)

# Save the index to disk
index.storage_context.persist(persist_dir=PERSIST_DIR)

storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)

index = load_index_from_storage(storage_context)

def query_index(index, question):
    query_engine = index.as_query_engine(
        similarity_top_k=3,  # Get top 3 most relevant results
        response_mode="no_text"  # This will return the raw Node objects
    )
    
    response = query_engine.query(question)
    
    for i, node in enumerate(response.source_nodes, 1):
        print(f"Answer {i}:")
        print(node.node.text)  # This will print the full text of each node
        print("\n")
    
# Your question
question = "Отрицательные показатели"

# Query the index
query_index(index, question)

#####################################################################
import fitz  # PyMuPDF
from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, LLMPredictor, ServiceContext
from llama_index.node_parser import SimpleNodeParser
from llama_index.embeddings import OpenAIEmbedding
from langchain.chat_models import ChatOpenAI
import os

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

def main():
    # Path to your PDF file
    pdf_path = "path/to/your/complex_document.pdf"
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Chunk the text
    chunks = chunk_text(text)
    
    # Create a custom reader
    class CustomReader(SimpleDirectoryReader):
        def __init__(self, chunks):
            self.chunks = chunks

        def load_data(self):
            return [{"text": chunk} for chunk in self.chunks]

    reader = CustomReader(chunks)
    documents = reader.load_data()
    
    # Create LLM predictor and embedding model
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"))
    embed_model = OpenAIEmbedding()
    
    # Create service context
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        embed_model=embed_model
    )
    
    # Create node parser
    node_parser = SimpleNodeParser.from_defaults()
    
    # Create index
    index = GPTVectorStoreIndex.from_documents(
        documents,
        service_context=service_context,
        node_parser=node_parser
    )
    
    # Save index to disk
    index.storage_context.persist("./storage")
    
    print("Index created and saved successfully.")

if __name__ == "__main__":
    main()
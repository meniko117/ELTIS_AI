import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SimpleNodeParser
import openai


# Set your OpenAI API key
openai.api_key = open_api_key

# Path to your document(s)
DOCUMENTS_DIR = r"C:\Users\134\Documents\for_Llama_index"

# Path to save the index
PERSIST_DIR = "./my_test_storage"


# Function to create index for each markdown file
def create_index_for_file(file_path, persist_dir):
    # Load the document from the file
    
    reader = SimpleDirectoryReader(
        input_files=[file_path]
    )    
    docs = reader.load_data()
    
    
    
    
    # Create a parser with custom chunk size and overlap
    parser = SimpleNodeParser.from_defaults(
        chunk_size=1024,  # Adjust this value as needed
        chunk_overlap=200  # Adjust this value as needed
    )
     
    # Parse the document into nodes
    nodes = parser.get_nodes_from_documents(docs)
    
    # Create the index
    index = VectorStoreIndex(nodes)
    
    # Save the index to a separate directory for each file
    index_dir = os.path.join(persist_dir, os.path.basename(file_path))
    os.makedirs(index_dir, exist_ok=True)
    index.storage_context.persist(persist_dir=index_dir)
    
    print(f"Index created and saved for file: {file_path}")


# Iterate over each markdown file in the directory
for file_name in os.listdir(DOCUMENTS_DIR):
    if file_name.endswith(".md"):  # Assuming files are markdown
        file_path = os.path.join(DOCUMENTS_DIR, file_name)
        create_index_for_file(file_path, PERSIST_DIR)

#########################################

# Function to load the index for a specific file and query it
def load_and_query_index(file_name, question):
    index_dir = os.path.join(PERSIST_DIR, file_name)
    storage_context = StorageContext.from_defaults(persist_dir=index_dir)
    index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine(
        similarity_top_k=3,  # Get top 3 most relevant results
        response_mode="no_text"  # This will return the raw Node objects
    )
    
    response = query_engine.query(question)
    
    # Initialize an empty string to store concatenated results
    concatenated_results = ""
    
    # Iterate over the response nodes and concatenate the results
    for i, node in enumerate(response.source_nodes, 1):
        # Concatenate the answer number and the text from the node
        concatenated_results += f"Answer {i}:\n{node.node.text}\n\n"
    
    # Optionally, you can return or print the concatenated result
    print(concatenated_results)
    return concatenated_results

# Example of querying a specific file
question = "Что содержит заголовок таблицы?"
file_name = "rukovodstvo_operatora_apm_eltis_markdown.md"  # Replace with your actual file name

load_and_query_index(file_name, question)
